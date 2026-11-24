# Detection Phase A — Technical Assessment, Candidate Matrix and Benchmark Plan

**Status:** Phase A research/design deliverable. No model or runtime is selected for production.  
**Repository baseline:** `feature/phase-0-foundation` at the time of assessment.  
**Scope:** Existing detector contract audit, model/runtime candidate evaluation, preliminary license screening, benchmark protocol and decision gates.  
**Important:** This is an engineering assessment, not legal advice. License conclusions must be confirmed against the exact source revision, checkpoint/artifact, dependencies, dataset terms and intended deployment by the organization's legal/compliance owner.

---

## 1. Executive outcome

Phase A confirms that the repository contains only a minimal detector protocol and a generic processing-engine lifecycle abstraction. It does not yet contain a concrete object-detection model, model artifact, runtime adapter, registry, model lifecycle manager, detection API, or real detection UI.

The architecture is suitable as a direction, but the current domain contract needs refinement before implementing an adapter. The candidate shortlist should prioritize models with clearly documented commercial/self-hosted terms and export/runtime options. Benchmark evidence must be generated on the actual deployment hardware and representative data; published vendor latency figures are not comparable enough to select a production model.

**No production model/runtime is approved by this assessment.** The initial shortlist for technical evaluation is:
1. RF-DETR Nano/Small/Medium/Large (Apache-2.0 claims for those exact variants; verify checkpoint-specific notices).
2. Official RT-DETR / RT-DETRv2 implementations (repository Apache-2.0; verify exact weights and all transitive assets).
3. Ultralytics YOLO family only if the organization explicitly accepts AGPL-3.0 obligations for the entire applicable work or obtains a written commercial license covering the intended use.
4. A torchvision/Detectron2-based baseline may be added if a specific architecture/checkpoint and its weight terms meet the task requirements; do not assume a framework license automatically licenses pretrained weights.

Runtime candidates:
- ONNX Runtime: candidate for a portable ONNX deployment; verify package build, provider availability and exact package licensing in the dependency review.
- OpenVINO: candidate where Intel CPU/iGPU/VPU acceleration is relevant; project is Apache-2.0, but validate device support and performance on the target machine.
- PyTorch: reference/evaluation runtime and potentially first deployment runtime where ecosystem/model support outweighs deployment footprint.
- NVIDIA TensorRT: optional later optimization for a compatible NVIDIA deployment; requires exact CUDA/driver/GPU compatibility and review of NVIDIA's applicable software license terms.

## 2. Repository audit — observed facts

Files inspected:

- `backend/src/visionai/domain/detection.py`
- `backend/src/visionai/domain/processing.py`
- `backend/src/visionai/services/image_analysis.py`
- `backend/src/visionai/api/v1/routes/images.py`
- `backend/src/visionai/core/config.py`
- `backend/pyproject.toml`
- `backend/.env.example`
- `docs/architecture/object-detection-engine.md`

### 2.1 Current detector port

The current `ObjectDetector` protocol exposes only:

- `predict(image: numpy.ndarray, confidence_threshold: float = 0.5) -> list[Detection]`

The current `Detection` dataclass has `label`, `confidence`, `x1`, `y1`, `x2`, and `y2`.

Observed gaps:

| Area | Current state | Required Phase B direction |
|---|---|---|
| Domain isolation | Domain imports NumPy and exposes ndarray | Replace with a framework-neutral image/input abstraction; keep NumPy at processing/infrastructure boundary |
| Class identity | Label only | Stable `class_id` plus immutable label-map metadata and resolved class name |
| Geometry | Four unvalidated floats | Explicit original-image coordinate convention, bounds validation, clipping policy and deterministic serialization |
| Confidence | Unvalidated float | Reject NaN/infinity and values outside [0, 1]; document score semantics |
| Lifecycle | No detector lifecycle methods | Application-scoped lifecycle manager with load/verify/warm-up/ready/drain/close states |
| Model identity | Not represented | Alias, immutable model version, artifact checksum and model family in result metadata |
| Runtime identity | Not represented | Runtime name/version and execution provider/device class |
| Capabilities | Not declared | Input shape/layout, color order, supported providers, batch/concurrency capability |
| Error contract | No typed detector errors | Stable internal error taxonomy mapped at API boundary |
| Concurrency | Not specified | Explicit per-model admission limit and verified runtime thread-safety |
| Pre/postprocessing | Not defined in port | Versioned deterministic preprocessing and output/coordinate restoration |
| Tests | No adapter contract suite | Shared conformance tests for every concrete adapter |

### 2.2 Image ingestion and pixel conventions

The current `decode_image` implementation returns a three-channel OpenCV BGR array after Pillow header verification and OpenCV decode. The current image-analysis endpoint has a process-local semaphore of two operations and offloads decode/analysis through `run_in_threadpool`.

Implications:

- Detection should reuse the same hardened image validation path, not introduce another decoder.
- The internal image abstraction must state BGR or RGB explicitly. Conversion should occur once at a documented pipeline boundary.
- Existing image-analysis concurrency must not be treated as a detection inference limit.
- The current endpoint reads up to `max_upload_bytes + 1`, but multipart parsing/body limits remain a separate ingress concern.
- Existing image-analysis behavior and response schema remain unchanged while detection is introduced separately.

### 2.3 Existing dependency baseline

The backend currently declares FastAPI, Uvicorn, python-multipart, pydantic-settings, OpenCV headless, NumPy and Pillow. No model framework or inference runtime is currently declared in `backend/pyproject.toml`.

This is beneficial: no model framework has been prematurely coupled to the base backend dependency set. Detection runtime dependencies should be optional extras or isolated deployment dependency groups, selected after the benchmark gate.

## 3. Model-family candidate matrix

This matrix is a shortlist for controlled evaluation, not a ranking of production suitability. Published COCO results are not interchangeable with performance or quality on the eventual product dataset.

| Candidate | Model family characteristics | License screening | Strengths to test | Risks / questions | Phase A disposition |
|---|---|---|---|---|---|
| RF-DETR Nano / Small / Medium / Large | Real-time DETR-style detector; published variants provide a range of size/accuracy trade-offs | RF-DETR repository states Apache-2.0 for package and Nano–Large detection variants. Verify the exact checkpoint's license/provenance and bundled components | Transformer-based alternative to one-stage YOLO; documented export/runtime paths; commercially usable under stated Apache terms | Checkpoint size, memory, CPU performance, preprocessing, custom-class fine-tuning requirements and export parity must be measured | **Priority candidate** |
| Official RT-DETR / RT-DETRv2 | Real-time end-to-end DETR family; official repository contains Paddle and PyTorch implementations | Official repository advertises Apache-2.0. This does not by itself prove every downloaded checkpoint/dataset component has identical terms | Strong reference candidate; PyTorch path; published T4/TensorRT figures for comparison only | Multiple implementation paths increase dependency complexity; verify exact weights, preprocessing and export parity | **Priority candidate** |
| Ultralytics YOLO (version/variant to be selected) | Mature real-time detector ecosystem with multiple model scales and export options | Ultralytics currently states AGPL-3.0 for its code/models by default and requires an applicable Enterprise license for closed-source/proprietary deployment. Confirm intended internal, SaaS, customer-facing and redistribution scope in writing | Broad ecosystem, deployment examples, model scale options and export formats | AGPL obligations may be incompatible with a proprietary product; Enterprise terms, scope and fees require vendor confirmation | **Conditional only** |
| torchvision detection models | Framework-integrated reference detectors and baselines | PyTorch framework license and each checkpoint/weight's own terms must be checked independently | Strong integration with PyTorch; useful reproducible reference baseline | Model selection, maintenance status, accuracy/speed and deployment/export effort vary by architecture | **Optional baseline** |
| Detectron2 / MMDetection families | Research and production-oriented detection model ecosystems | Check repository license, model zoo checkpoint license, dataset terms and third-party components separately | Broad architecture coverage and research reproducibility | Potentially larger dependency surface and more complex deployment than a narrow inference adapter | **Optional research baseline** |

### 3.1 License interpretation rules

- A repository license is not automatic proof that all model weights, training datasets, tokenizer/configuration files, export tools or third-party dependencies share the same license.
- Record license identifiers and source URLs per artifact, not only per Python package.
- Preserve required notices, attribution, patent clauses and redistribution terms.
- For AGPL/commercial dual-license offerings, obtain written confirmation of the license scope, legal entity, internal users, deployment mode, derivative/fine-tuned models, term, renewal and production rights.
- Do not rely on marketing summaries alone; archive the exact license text and order form/contract applicable on the acquisition date.
- Dataset licensing and model-weight licensing are separate reviews.
- No legal conclusion about whether a specific deployment is a derivative work is made by this engineering document.

## 4. Inference runtime candidate matrix

| Runtime | Primary role | Hardware/provider direction | Operational characteristics | License / compliance review | Phase A disposition |
|---|---|---|---|---|---|
| ONNX Runtime | Portable inference for exported ONNX graphs | CPU and multiple execution providers, including CUDA, TensorRT, OpenVINO, DirectML and others; exact support varies by package/build/provider | Attractive adapter boundary and portable artifact format; execution-provider fallback/partitioning and operator coverage must be inspected | Verify exact runtime package license, bundled native libraries, provider packages and redistribution notices for the selected version | **Priority runtime candidate** |
| OpenVINO Runtime | Optimized inference in Intel-oriented environments | Intel CPU, integrated/discrete GPU and other supported devices depending on release/platform | Can provide CPU and Intel-device optimization; device/plugin behavior and supported ops require target-machine tests | OpenVINO project is Apache-2.0; audit bundled third-party components and package notices | **Priority if Intel hardware is confirmed** |
| PyTorch eager/runtime | Reference implementation, model evaluation and potentially direct serving | CPU and compatible GPU backends; platform/version-specific | Best compatibility for models whose official path is PyTorch; may have larger runtime footprint and Python dependency surface | PyTorch repository uses a BSD-style license with additional notices; review exact release and third-party packages | **Required evaluation baseline where model requires it** |
| NVIDIA TensorRT | NVIDIA GPU-specific optimized deployment | Compatible NVIDIA GPUs, drivers, CUDA and TensorRT versions | Can deliver optimized engines; build artifacts are hardware/software-stack sensitive and need reproducible build metadata | NVIDIA SDK is governed by NVIDIA software license terms; review the exact TensorRT product (standard vs RTX), version and redistribution rights | **Optional optimization after baseline** |

### 4.1 Important runtime distinctions

- ONNX is an interchange/artifact format; ONNX Runtime is an inference engine.
- CUDA is a GPU compute platform/runtime stack, not an object-detection model.
- TensorRT is an NVIDIA inference optimization/runtime SDK; it is not a model architecture.
- OpenVINO is an inference toolkit/runtime with its own device plugins and supported-operator constraints.
- PyTorch is a framework/runtime ecosystem; its model code and checkpoint provenance still need independent review.
- An exported model may produce numerically different outputs from its source framework. Export parity is a release gate, not an assumption.

## 5. Candidate evaluation and down-selection

### 5.1 Hard gates (must pass)

A candidate is disqualified from production selection if any of these remain unresolved:

1. The exact model checkpoint cannot be obtained from a traceable source.
2. Commercial/internal/self-hosted rights are unclear for the intended deployment.
3. Required object taxonomy cannot be represented or fine-tuned with a lawful dataset.
4. Required target hardware/provider is unsupported.
5. Preprocessing/postprocessing behavior cannot be reproduced and tested.
6. Exported artifact output is materially inconsistent with its reference implementation.
7. Memory use exceeds the deployment budget under the expected concurrency.
8. Security or supply-chain review identifies an unmitigated critical issue.

### 5.2 Weighted scorecard

After hard gates pass, score each model/runtime configuration from 1 (poor) to 5 (excellent). Weights below are proposed evaluation weights, not measured results.

| Criterion | Weight |
|---|---:|
| Task quality on the product evaluation dataset (mAP, precision, recall and per-class performance) | 30% |
| End-to-end latency and throughput on target hardware | 20% |
| Peak RAM/VRAM and behavior under concurrency | 15% |
| License clarity and commercial deployment rights | 15% |
| Runtime portability, export parity and supported operators | 10% |
| Maintenance, documentation and operational complexity | 5% |
| Artifact size, cold start and warm-up | 5% |
| **Total** | **100%** |

Do not compute a final weighted score until hard gates pass and benchmark evidence is collected. A high aggregate score must never override a failed legal, security or hardware compatibility gate.

## 6. Benchmark protocol

### 6.1 Benchmark objectives

The benchmark must answer:

- Which model meets the product's per-class quality requirements?
- What is end-to-end latency, not only model-forward latency?
- What throughput is sustainable at the expected concurrency?
- What are peak host RAM and accelerator memory requirements?
- What is cold-start and warm-up cost?
- Does ONNX/OpenVINO/TensorRT export preserve acceptable quality?
- How does the service behave when capacity is exhausted or a runtime fails?

### 6.2 Dataset protocol

Create a versioned, access-controlled evaluation dataset representative of intended use:

- Include the actual object categories and expected scene diversity.
- Include small, medium and large objects; occlusion; clutter; lighting variation; blur; rotations; and difficult negatives.
- Use a documented annotation policy and perform quality review of labels.
- Split by source/capture session or another leakage-resistant grouping, not only random near-duplicate images.
- Keep train/validation/test sets disjoint. Never tune thresholds on the final holdout test set.
- Record dataset version, source, collection date, consent/rights, retention policy, annotation tool/version and checksum.
- Do not place private or licensed images in public Git history.
- If COCO is used as a public sanity benchmark, record its exact split and license; it does not replace the product-specific evaluation set.

### 6.3 Quality metrics

Report at minimum:

- mAP@[.50:.95] and AP50 using a stated evaluation implementation.
- Per-class AP and support count.
- Precision and recall at the selected operating threshold.
- Confusion/error analysis: false positives, false negatives, duplicate boxes and localization failures.
- Performance by object size and important environmental subgroup.
- Calibration/score distribution where confidence is used for user-facing decisions.

The model-selection decision must set minimum per-class and aggregate acceptance thresholds before final evaluation. Do not select solely by aggregate mAP if critical classes have poor recall.

### 6.4 Performance metrics

Measure and report:

- Cold process start and model load duration.
- Warm-up duration and first-request latency.
- Preprocessing, model execution and postprocessing durations separately.
- End-to-end p50, p95 and p99 latency.
- Sustainable requests/second and images/second at batch size 1 initially.
- Concurrency sweep at 1, 2, 4 and higher levels only within the known hardware budget.
- Peak RSS/host RAM and accelerator memory.
- CPU/GPU utilization and thermal/power throttling where observable.
- Timeout, overload rejection and error rates.
- Long-running stability test and memory growth.

Do not report only average latency. Include sample count, warm-up policy, image dimensions, runtime/provider versions, precision mode, batch size, concurrency, device and environment.

### 6.5 Controlled variables

For a fair comparison:

- Use the same dataset and exact image bytes for every candidate.
- Use the same target input dimensions where the model permits; also test native recommended sizes as a separate track.
- Fix confidence threshold, NMS/IoU behavior and max detections, documenting differences where architectures do not expose equivalent controls.
- Pin model artifact checksums, source revisions, package versions and driver/runtime versions.
- Run repeated trials after warm-up; report distributions and confidence intervals where useful.
- Keep model loading outside steady-state inference timing, but report it separately.
- Benchmark preprocessing and postprocessing, not just the model forward pass.
- Compare FP32 and reduced precision only when supported; validate quality degradation.
- Run CPU and accelerator tracks independently. Never compare a vendor T4 TensorRT result to a CPU result as if conditions were equivalent.

### 6.6 Test matrix

| Track | Model | Runtime | Device | Precision | Purpose |
|---|---|---|---|---|---|
| A | Candidate checkpoint | Native framework | CPU | FP32 | Reference correctness and CPU baseline |
| B | Same checkpoint/export | ONNX Runtime CPU | CPU | FP32 | Portability and CPU performance |
| C | Same exported artifact | OpenVINO | Supported Intel device | Supported FP32/FP16/INT8 | Intel hardware candidate |
| D | Same exported artifact | ONNX Runtime CUDA | Compatible NVIDIA GPU | FP32/FP16 | NVIDIA general GPU candidate |
| E | Same model where supported | TensorRT | Compatible NVIDIA GPU | FP16/INT8 as validated | Optional optimized deployment |
| F | Same images and preprocessing | All passing configurations | Target device | As configured | Output parity and quality comparison |

Not every model supports every track. Unsupported cells should be marked N/A with evidence, not silently omitted.

### 6.7 Reproducibility artifacts

Every benchmark run must archive:

- Benchmark run ID and timestamp.
- Git commit SHA of the benchmark harness.
- Model manifest and artifact SHA-256.
- Runtime/provider and dependency lock versions.
- Hardware inventory and OS/driver details.
- Dataset version and checksum.
- Full configuration (input size, thresholds, NMS, batch, concurrency, precision).
- Raw per-image outputs or a privacy-safe derived record.
- Metrics summary, logs and failure records.
- Environment/container definition and exact invocation command.

## 7. Proposed benchmark harness design

The harness should be independent of FastAPI initially, so model/runtime comparisons are not distorted by HTTP overhead.

Logical components:

- `DatasetReader`: loads immutable image/annotation records.
- `ModelManifestLoader`: validates model metadata and artifact checksum.
- `CandidateRunner`: loads one model/runtime configuration and exposes a common prediction contract.
- `PreprocessAdapter`: applies the candidate's declared preprocessing.
- `InferenceTimer`: captures warm-up and steady-state timings separately.
- `OutputNormalizer`: converts outputs to the common original-image coordinate convention.
- `Evaluator`: computes detection metrics using a pinned evaluation implementation.
- `ResourceSampler`: captures process RAM and supported accelerator telemetry.
- `ReportWriter`: emits machine-readable JSON/CSV and a human-readable Markdown report.

Harness rules:

- Do not download weights implicitly during a benchmark run.
- Require explicit local artifact paths from a controlled artifact directory.
- Verify SHA-256 before every run.
- Never mutate the source dataset or original images.
- Separate correctness/evaluation mode from throughput mode.
- Use deterministic configuration and record nondeterministic runtime settings.
- Keep optional hardware telemetry failures visible; never fabricate missing measurements.

## 8. Model artifact manifest — required fields

Each model checkpoint promoted for evaluation or deployment must have a manifest with:

- `model_id`, public alias and immutable version.
- Model family, architecture and variant.
- Source repository, source revision/tag and acquisition date.
- Artifact filename, format, byte size and SHA-256.
- Model/checkpoint license identifier and exact license URL or archived text.
- Training dataset provenance and license references where known.
- Label-map version/checksum and class ID mapping.
- Input dimensions, color order, tensor layout, dtype and normalization.
- Resize/letterbox policy and interpolation method.
- Output format, confidence semantics, NMS policy and coordinate convention.
- Export provenance and source-framework/runtime versions.
- Tested runtime/provider combinations and hardware evidence.
- Evaluation dataset version and benchmark report reference.
- Approval state and reviewer.

A model cannot be marked approved if license/provenance fields are unknown.

## 9. Security, privacy and compliance gates

- Model artifacts are supply-chain inputs: verify checksums and source provenance.
- Do not accept arbitrary model URLs, Python pickles or user-defined code.
- Review model licenses separately from framework/runtime licenses.
- Review dataset rights, consent and retention independently from model rights.
- Do not upload private evaluation images to third-party benchmark services without authorization.
- Keep model artifacts out of Git and public CI artifacts unless explicitly approved.
- Scan pinned dependencies and preserve third-party notices.
- For NVIDIA runtimes, review the exact product-specific software agreement and any redistribution/benchmark-publication restrictions.
- Treat all vendor benchmark claims as informational until reproduced on target hardware.

## 10. Phase A exit criteria

Phase A is complete when all of the following are true:

1. Current detector and processing contracts have an evidence-based audit record.
2. Contract gaps and required changes are recorded without prematurely implementing an inference engine.
3. Model candidate matrix includes model family, exact variant, source, checkpoint license and unresolved questions.
4. Runtime matrix distinguishes runtime, artifact format, execution provider and hardware.
5. License screening is recorded for code, checkpoint, datasets and transitive components separately.
6. A representative dataset plan and annotation policy are approved.
7. Benchmark protocol and scorecard are versioned.
8. Target hardware and workload profile are supplied.
9. Hard-gate failures and decision owners are explicit.
10. A model/runtime selection decision record is approved before Phase B implementation.

## 11. Target hardware profile and remaining product inputs

### 11.1 Hardware supplied for initial evaluation

The user supplied the following Task Manager inventory on 2026-11-24. This is recorded as the **initial target/evaluation machine**, not as proof that it is the final production deployment host.

| Component | Supplied value | Assessment note |
|---|---|---|
| CPU | 12th Gen Intel Core i7-12700K | 12 physical cores / 20 logical processors |
| RAM | 32 GB DDR4, reported speed 2133 MHz | Adequate for initial single-model evaluation; concurrency headroom must be measured |
| GPU | NVIDIA GeForce RTX 3060 Ti | 8 GB dedicated VRAM |
| NVIDIA driver | **576.28** (confirmed by `nvidia-smi`, 2026-11-24) | `nvidia-smi` reports CUDA compatibility version **12.9**; this is the driver's supported CUDA level, not proof that CUDA Toolkit 12.9 or cuDNN is installed |
| Storage | Samsung SSD 980, nominal 500 GB (466 GB formatted) | Free space was not supplied; reserve model/artifact and benchmark-output capacity explicitly |
| Graphics API | DirectX 12, Feature Level 12.1 | Does not establish installed CUDA Toolkit/cuDNN versions |
| OS | Windows 10 Enterprise LTSC 21H2, OS build 19044.1288 | Windows target is now identified; exact support must still be checked against the chosen CUDA/ORT/PyTorch/OpenVINO release matrices |

The machine is a credible candidate for initial CPU-versus-NVIDIA-GPU inference benchmarking. The 8 GB VRAM capacity makes model size, input resolution, precision, batch size and concurrent inference important measured constraints. No FPS, latency, throughput or maximum concurrency is inferred from the inventory. The earlier Task Manager display-driver string (`32.0.15.7628`) is superseded for CUDA compatibility assessment by the exact `nvidia-smi` output: NVIDIA-SMI 576.28, Driver Version 576.28, CUDA Version 12.9. At capture time the GPU was in WDDM mode, at 42°C, using 966 MiB of 8192 MiB VRAM, with 4% utilization. These are point-in-time observations, not capacity or throughput benchmarks.

### 11.2 Initial benchmark tracks for this hardware

With the confirmed NVIDIA driver 576.28 / reported CUDA compatibility 12.9 and Windows 10 Enterprise LTSC 21H2, the first controlled benchmark should compare. Exact PyTorch/ONNX Runtime package compatibility still must be checked against the selected release's CUDA/cuDNN build requirements:

1. Candidate model's native PyTorch implementation on CPU as a correctness/reference path.
2. The same model on PyTorch with NVIDIA CUDA, where the exact PyTorch build supports the installed driver/runtime.
3. The same exported ONNX artifact on ONNX Runtime CPU.
4. The same exported ONNX artifact on ONNX Runtime CUDA Execution Provider, after matching its CUDA and cuDNN requirements.
5. OpenVINO CPU as an optional Intel CPU comparison after confirming the OS/package support for the selected OpenVINO release.

TensorRT remains an optional optimization track after a baseline has been measured. Do not add CUDA, cuDNN, PyTorch, ONNX Runtime GPU or TensorRT dependencies to the base application until the exact OS, package versions and deployment requirements are pinned.

### 11.3 Inputs still required from product/operations

The following values remain unknown and must not be inferred:

- Whether this computer is the final production host, a development workstation, or a benchmark-only machine.
- Whether CUDA Toolkit and cuDNN are installed; if so, their exact versions. `nvidia-smi` alone does not establish this. `where nvcc` returned `INFO: Could not find files for the given pattern(s).`; this establishes only that `nvcc` was not found through the current CMD PATH, not that every CUDA runtime component is absent.
- Free SSD capacity reported by `wmic logicaldisk` on 2026-11-24: C: 392,483,848,192 bytes free (approximately 365.4 GiB); E: 726,165,950,464 bytes free (approximately 676.1 GiB). These are point-in-time values; filesystem allocation and future usage can change them.
- Whether deployment is on-premises, cloud, edge or mixed.
- Typical and maximum input image width/height.
- Expected concurrent requests and peak requests/second.
- Required object classes and whether COCO classes are sufficient or custom classes are required.
- Quality priorities and critical per-class recall/precision.
- Latency target (p50/p95/p99) and throughput target.
- Whether the product is proprietary/closed-source, internal-only, customer-facing, SaaS, redistributed or open-source.
- Whether model fine-tuning is planned and who owns/controls training data.

Until these are known, candidate ranking remains provisional and no runtime dependency should be added to the production backend.

## 12. References reviewed

The following vendor/project pages were consulted during this assessment. Their current terms and exact artifact-level notices must be rechecked when a candidate is acquired.

- Ultralytics licensing: https://www.ultralytics.com/license
- Ultralytics Enterprise Software License terms: https://www.ultralytics.com/legal/enterprise-software-license
- Official RT-DETR repository and license: https://github.com/lyuwenyu/RT-DETR
- RF-DETR repository, variant license matrix and benchmark methodology: https://github.com/roboflow/rf-detr
- ONNX Runtime execution providers: https://onnxruntime.ai/docs/execution-providers/
- OpenVINO repository and Apache-2.0 license: https://github.com/openvinotoolkit/openvino
- PyTorch project: https://pytorch.org/projects/pytorch/
- NVIDIA TensorRT documentation: https://docs.nvidia.com/deeplearning/tensorrt/latest/
- NVIDIA TensorRT software license agreement: https://docs.nvidia.com/deeplearning/tensorrt/latest/reference/sla.html

---

## 13. Decision record

**Decision:** No production model or runtime selected in Phase A.

**Shortlist for the first benchmark:** RF-DETR Nano/Small and RT-DETRv2-S as license-screened candidates, with one PyTorch reference path and an ONNX Runtime CPU path where export support is verified. Add OpenVINO only if the target hardware supports it. Treat Ultralytics YOLO as conditional on explicit license acceptance or an appropriate commercial agreement.

**Reason:** Current target hardware, product taxonomy, workload, dataset and deployment/license posture are not specified. Choosing a model now would be an unsupported assumption.

**Next phase:** Once target hardware and product constraints are supplied, freeze the benchmark matrix, obtain approved artifacts, run baseline correctness/performance tests, and issue a separate model/runtime selection ADR. Only then implement the first concrete adapter.
