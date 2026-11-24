# Object Detection Engine — Product Architecture

**Status:** Approved target architecture; implementation has not started.  
**Scope:** Product-level architecture and delivery contract for image object detection.  
**Platform:** VisionAI-Platform modular monolith; Python 3.12+, FastAPI, OpenCV, React and TypeScript.  
**Decision policy:** Model family, runtime, hardware profile, benchmark thresholds and production deployment profile remain decision gates until workload and target hardware are measured.

---

## 1. Executive summary

The Object Detection Engine is a capability module that accepts a validated image, executes a configured object-detection model, and returns stable, model-independent detection results. The public API, application use cases, domain model and frontend must not be coupled to YOLO, PyTorch, ONNX Runtime, OpenVINO, TensorRT or another vendor/framework.

The architecture separates:

1. **Detection contract:** input/output semantics, coordinate system, confidence semantics, errors and versioning.
2. **Application orchestration:** request policy, model selection, execution mode and response composition.
3. **Detection pipeline:** image normalization, preprocessing, inference invocation, postprocessing and result validation.
4. **Model/runtime adapter:** framework-specific model loading, tensor execution, device selection and output decoding.
5. **Model operations:** artifact provenance, integrity, configuration, lifecycle, readiness, warm-up, capacity and controlled replacement.

The first delivery should be a bounded synchronous image-detection use case. Asynchronous jobs, batch inference, video, tracking, streaming, model training and user-managed model uploads are separate capabilities and are excluded from the first release.

## 2. Product goals and non-goals

### 2.1 Goals

- Provide one stable detection API regardless of the selected model/runtime.
- Return object instances with class identity, confidence and bounding boxes in a documented coordinate system.
- Make preprocessing and postprocessing explicit, deterministic and testable.
- Load models through controlled lifecycle management, not per request.
- Support CPU execution as a capability; support accelerator execution only after runtime and hardware verification.
- Bound memory, image dimensions, inference concurrency, queueing, batch size and request duration.
- Include model identity and immutable version in results for reproducibility.
- Permit additional model/runtime adapters without rewriting application or API layers.
- Require measurable quality, latency, throughput and resource evidence before production claims.

### 2.2 Non-goals for the first release

- Training, fine-tuning or dataset labeling.
- Arbitrary model uploads or arbitrary Python/plugin execution by users.
- Multi-model ensembles or automatic model selection based on image content.
- Video ingestion, object tracking, re-identification, segmentation, OCR, pose estimation or camera streaming.
- Distributed GPU scheduling, autoscaling, multi-node inference or a separate inference microservice.
- Durable jobs, result history, billing, quotas and tenant administration unless separately approved.
- Any promise of FPS, latency, accuracy or supported object taxonomy before representative evaluation.

## 3. Architectural placement

The engine remains inside the existing modular monolith. It is a separately bounded capability, not a new microservice.

~~~text
Browser / API Client
        |
        v
FastAPI Detection Route
        |
        v
DetectObjects Use Case
  |      |        |
  |      |        +---- Detection Policy / Model Selection
  |      |
  |      +------------- Validated Image Input
  |
  v
ObjectDetectionService
        |
        +---- Preprocessor
        |
        +---- ObjectDetector Port
        |         |
        |         +---- Runtime Adapter
        |                   |
        |                   +---- Model Artifact + Runtime Session
        |
        +---- Postprocessor
        |
        +---- Detection Result Validator
        |
        v
Stable Detection Response DTO
~~~

### 3.1 Dependency rules

- API depends on application contracts and DTOs, not runtime libraries.
- Application depends on domain ports and policy abstractions.
- Domain owns stable value objects, detection semantics and adapter ports.
- Processing owns image/tensor transformations and pipeline composition.
- Infrastructure owns concrete runtime adapters, artifact access, device discovery and telemetry exporters.
- Frontend consumes only the versioned API contract.
- Concrete model/runtime packages must not be imported by route handlers or domain modules.
- The public contract must not expose NumPy arrays, framework tensors or vendor-specific result objects.

Suggested logical package boundaries (adapt to the actual source tree during implementation):

~~~text
visionai/
  api/v1/routes/detections.py
  application/detection/
    commands.py
    use_cases.py
    policies.py
  domain/detection/
    entities.py
    value_objects.py
    ports.py
    errors.py
  processing/detection/
    pipeline.py
    preprocessing.py
    postprocessing.py
    validation.py
  infrastructure/detection/
    registry.py
    lifecycle.py
    artifacts.py
    runtimes/
      onnx_runtime/
      pytorch/
  schemas/detection.py
~~~

These are target boundaries, not a claim that these files exist today. Implementation must inspect and align with the actual repository layout.

## 4. Core contracts

### 4.1 Input contract

The application use case receives an already validated and decoded image abstraction plus explicit detection options. It must not receive an unbounded raw request body.

Required properties:

- Pixel data with documented channel order. Canonical internal representation: RGB, unless profiling or the selected adapter requires another internal tensor representation.
- Original image width and height.
- Validated source format and media metadata where relevant.
- Model selector: approved model alias or immutable version; never a client-supplied filesystem path or arbitrary URL.
- Optional confidence threshold and class filter, validated against server policy.
- Optional maximum detections, bounded by server-side limits.
- Correlation/request identifier supplied by the application boundary.

The image contract must define buffer ownership and mutability. Preprocessing must not mutate a shared source buffer in place unless explicitly documented and tested.

### 4.2 Detection result

Each detection represents one object hypothesis:

- **class_id:** integer class identifier from the selected model label map.
- **class_name:** resolved label from immutable model metadata.
- **confidence:** finite numeric value in the inclusive range [0, 1], with semantics documented for the selected model adapter.
- **bounding_box:** x_min, y_min, x_max, y_max in pixel coordinates relative to the original decoded image.

Coordinate convention:

- Origin is the top-left corner.
- X increases right; Y increases down.
- Coordinates are expressed in original-image pixels, not resized tensor pixels.
- The box is half-open: [x_min, x_max) × [y_min, y_max).
- Bounds must satisfy 0 <= x_min < x_max <= image_width and 0 <= y_min < y_max <= image_height.
- The postprocessor must reverse letterboxing, scaling, cropping and padding before emitting public results.
- Rounding policy must be deterministic. Preserve floating-point coordinates internally and serialize a stable numeric representation.

Detection ordering must be deterministic for equivalent model outputs: descending confidence, then class ID, then coordinates as stable tie-breakers. NMS behavior, IoU threshold, class-aware/class-agnostic mode and maximum output count belong to model/pipeline configuration and must be observable in model metadata.

### 4.3 Response envelope

The API response should include:

- request_id
- image: original width, height and accepted media type
- model: public model alias, immutable version, model family and runtime identifier/version
- inference: duration in milliseconds and device class; do not expose sensitive host/device identifiers
- detections: ordered detection list
- summary: total count and optional per-class counts

Do not include internal filesystem paths, artifact URLs, secret configuration, raw tensor output, stack traces or private infrastructure details.

A successful inference with no objects is a valid success response with an empty detections array. It is not a 404 or an inference failure.

## 5. Public API design

The first public capability is a synchronous image endpoint:

- **POST /api/v1/detections**
- Content type: multipart/form-data
- Required part: image file.
- Optional fields: approved model alias/version, confidence threshold, bounded maximum detections and class filter.
- Response: stable detection response envelope.

The existing **POST /api/v1/images/analyze** endpoint remains independent and backward-compatible. Detection must not silently change the semantics or response schema of basic image analysis.

### 5.1 Request policy

- Reuse the existing image-ingestion validation path; do not implement a second, weaker decoder.
- Enforce upload bytes, dimensions, total pixels, supported formats and bounded processing concurrency.
- Validate numeric options and reject NaN/infinity. Clamp or reject out-of-range values according to explicit API policy.
- The client may select only model aliases exposed by server policy.
- Default model selection is server configuration, not an implicit hard-coded model in the route.
- Apply request timeout and bounded inference concurrency.
- Return a stable error envelope with a machine-readable code and safe message.

### 5.2 Future asynchronous API

Long-running jobs may later use a separate resource-oriented contract:

- **POST /api/v1/detection-jobs** — create a job and return 202 Accepted with a job ID.
- **GET /api/v1/detection-jobs/{job_id}** — retrieve status/result.
- **DELETE /api/v1/detection-jobs/{job_id}** — request cancellation where supported.

This is a future direction only. Do not add Redis, a queue, database tables or job endpoints until measured latency/workload or product requirements justify durable asynchronous execution. A process-local background task is not a durable job system.

## 6. Model and runtime abstraction

### 6.1 Separate model family from runtime

YOLO is a model-family/ecosystem label, not an inference runtime. The architecture must distinguish:

- **Model family/architecture:** for example, a selected YOLO generation or another detector architecture.
- **Artifact format:** for example, ONNX or framework-native weights.
- **Runtime:** for example, ONNX Runtime, PyTorch, OpenVINO or TensorRT.
- **Execution provider/device:** CPU or a specifically supported accelerator provider.
- **Adapter:** VisionAI implementation translating the stable contract to the selected model/runtime.

A model may have multiple exported artifacts and runtime profiles. They are separate immutable deployment configurations and must be benchmarked independently.

### 6.2 Detector port

The domain-facing detector port should expose lifecycle-safe operations conceptually equivalent to:

- load(model_spec, runtime_config) -> loaded detector capability
- predict(input_tensor, inference_options) -> raw model output
- health() -> readiness/capability status
- close() -> release runtime resources

The exact Python protocol and sync/async shape must be selected after profiling the chosen runtime. Do not force asynchronous methods around a synchronous native call if that obscures execution control. The application boundary must ensure inference does not block the ASGI event loop.

The port must declare supported input constraints, layout, batch size, device providers, class metadata, output format and whether concurrent calls are safe. Unsupported capabilities must fail during configuration/readiness validation, not midway through a user request.

### 6.3 Adapter responsibilities

Each concrete adapter owns:

- Runtime session creation and destruction.
- Model artifact compatibility checks.
- Input tensor layout, dtype, normalization and channel conversion.
- Model-specific output parsing.
- Conversion into a framework-neutral raw detection representation.
- Runtime/device errors translated into stable internal errors.
- Capability declaration and runtime version reporting.

The adapter must not own HTTP status codes, user authorization, database persistence, frontend formatting or arbitrary model-selection policy.

### 6.4 Runtime selection gate

Do not choose a production model/runtime solely by popularity or theoretical benchmark. Compare candidates using the same representative image corpus and target hardware.

Required selection inputs:

1. Target operating system and deployment environment.
2. Exact CPU/GPU model, available VRAM/RAM, driver and supported accelerator stack.
3. Expected image dimensions, formats, batch size, concurrent users and peak requests/second.
4. Accuracy priorities and required object classes.
5. Maximum acceptable p50/p95 latency and throughput.
6. Model license and redistribution/commercial-use constraints.
7. Artifact size, cold-start time, warm-up time, memory footprint and operational complexity.

Candidate runtimes may include ONNX Runtime, PyTorch, OpenVINO and TensorRT where compatible. They are candidates, not approved dependencies. Select one initial runtime after a reproducible benchmark and compatibility/license review. Keep a CPU fallback only if it is tested and operationally supportable.

## 7. Model artifact and registry design

### 7.1 Immutable model specification

Every deployable model version must have a manifest containing at least:

- Public model name/alias and immutable version.
- Model family and architecture variant.
- Artifact format and relative artifact reference.
- SHA-256 checksum.
- Source/provenance and acquisition timestamp.
- License identifier and compliance review status.
- Input shape constraints, color order, tensor layout, dtype, normalization, resize/letterbox policy.
- Label map and label-map checksum/version.
- Output schema and coordinate convention.
- Confidence interpretation, NMS configuration and default thresholds.
- Supported runtimes/providers and tested versions.
- Evaluation dataset/version and benchmark report reference.

The manifest is configuration data, not executable code. Validate it strictly at startup/deployment time.

### 7.2 Artifact handling

- Do not commit model weights or large binaries to Git.
- Do not download arbitrary model artifacts on application startup.
- Provision artifacts through a controlled deployment/artifact process.
- Verify checksum before loading.
- Store artifacts in a read-only or tightly permissioned location.
- Do not allow user-supplied paths, URLs, pickle files or custom code into the model-loading path.
- Record artifact provenance and license before enabling a model in production.

### 7.3 Registry and aliasing

The registry maps a public alias to a specific immutable model specification. A deployment configuration can promote an alias from one immutable version to another only through an explicit rollout/change process.

Never mutate the meaning of an immutable version. Keep rollback possible by retaining the prior known-good artifact and configuration. The first implementation may use a validated local manifest/configuration provider; a database-backed registry is not required.

## 8. Model lifecycle and readiness

Model loading must be an explicit application lifecycle operation, not part of every request.

Expected states:

- UNCONFIGURED: no valid model specification is configured.
- RESOLVING: manifest and artifact are being resolved.
- VERIFYING: checksum, format and compatibility checks are running.
- LOADING: runtime session is being created.
- WARMING: optional bounded warm-up is running.
- READY: model can accept requests.
- DEGRADED: model is loaded but a declared capability/resource is unavailable.
- FAILED: model cannot safely serve requests.
- DRAINING: new work is rejected while in-flight work completes.
- CLOSED: runtime resources have been released.

Requirements:

- Liveness must not depend on a model being loaded.
- Readiness must report whether the configured detection capability can serve traffic.
- Do not report ready before artifact verification, load and required warm-up complete.
- Startup failure policy (fail application startup vs. disable detection while serving unrelated image analysis) must be explicit in deployment configuration.
- Shutdown must stop admission, drain or cancel in-flight work according to a documented timeout, and release runtime resources.
- Model replacement must use a controlled drain/swap procedure; never close a session while requests are using it.
- Avoid hidden module-level model singletons. Use an application-scoped lifecycle manager with explicit ownership.

## 9. Execution, concurrency and resource control

Inference is resource-intensive. The service must use explicit admission control.

Controls to define and measure:

- Maximum upload bytes and decoded pixels (reuse existing image policy).
- Maximum inference input dimensions and model-specific resize policy.
- Maximum detections per image.
- Maximum inference concurrency per loaded model and per process.
- Queue capacity and overload response, if a bounded queue is introduced.
- Request/inference timeout.
- CPU thread count and accelerator memory budget.
- Warm-up and cold-start behavior.
- Shutdown/drain timeout.

Do not infer that the existing image-analysis semaphore safely controls model inference. Detection has its own resource profile and needs a separately configured limit.

Initial synchronous behavior should reject overload quickly with a stable retryable error rather than accumulate unbounded requests. A queue may be introduced only with bounded capacity, queue timeout, cancellation semantics and metrics. GPU execution must not be assumed thread-safe; verify runtime/provider behavior and default to serialized access per session until concurrency safety is demonstrated by tests and measurements.

Do not promise multi-process GPU sharing or global concurrency guarantees from a process-local semaphore. Deployment replicas and worker counts must be included in capacity planning.

## 10. Error taxonomy

Use stable internal error codes mapped to safe HTTP responses at the API boundary. At minimum distinguish:

- Invalid/unsupported image input.
- Image exceeds configured resource limits.
- Invalid detection options.
- Unknown or disabled model alias/version.
- Model not ready.
- Model artifact missing or checksum mismatch.
- Runtime/provider unavailable or incompatible.
- Inference timeout.
- Inference capacity exhausted.
- Invalid/non-finite model output.
- Internal inference failure.

Do not return raw framework exceptions, paths, provider diagnostics or stack traces to clients. Preserve diagnostic context in structured server logs with request correlation. A no-detection result is not an error.

## 11. Security and supply-chain controls

- Treat image uploads and model artifacts as untrusted inputs.
- Reuse the hardened image decoder and resource checks.
- Never expose arbitrary model-loading or Python execution endpoints.
- Restrict artifact directory permissions and verify checksums.
- Review model and dataset licenses before use or redistribution.
- Pin compatible runtime dependencies and scan them through the repository dependency-security process.
- Avoid leaking model paths, hostnames, GPU identifiers, environment variables or secrets.
- Apply authentication/authorization when introduced; model administration must be separate from ordinary inference permission.
- Apply per-user/tenant quotas only when identity and tenant boundaries are implemented and tested.
- Ensure errors and logs do not include uploaded image bytes or unnecessary personal/sensitive content.

## 12. Observability and operational signals

Use structured logs and metrics with request/model correlation. Do not log image contents.

Recommended metrics:

- Detection requests by outcome and model version.
- End-to-end latency and inference latency (p50/p95/p99).
- Preprocessing and postprocessing duration.
- Model load and warm-up duration.
- In-flight inference count, admission rejections and queue wait time (if applicable).
- CPU/RAM and accelerator utilization/memory where supported.
- Input image dimensions and pixel-count buckets, not raw image content.
- Runtime/provider failures, timeouts, invalid model outputs and artifact verification failures.
- Detection-count distribution, with care to avoid high-cardinality labels.

Health/readiness output must be safe and concise. Do not expose internal artifact locations or detailed machine configuration publicly.

## 13. Frontend product behavior

The web client should consume the stable API response and provide:

- Image preview and upload progress.
- Model selector only when the server advertises more than one enabled model.
- Confidence threshold controls only within server-approved bounds.
- Clear processing/loading, success, empty-result, validation-error, capacity, timeout and retry states.
- Bounding-box overlay aligned to the original preview, accounting for responsive scaling and device-pixel ratio.
- Class label and confidence display with accessible contrast and non-color-only distinctions.
- Detection summary and a way to hide/show overlays.
- A clear distinction between “no objects detected” and “detection failed”.

Do not expose runtime names or low-level model parameters as user-facing controls unless a product requirement justifies them. Do not present mock detections as real inference.

## 14. Testing and evaluation strategy

### 14.1 Unit tests

- Coordinate conversion for resize, letterbox, crop and padding.
- Bounding-box validation and clipping.
- Confidence finite/range validation.
- Deterministic ordering and NMS policy.
- Label-map resolution and unknown class handling.
- Manifest schema, checksum verification and invalid configuration.
- Lifecycle state transitions and shutdown behavior.
- Capacity admission, timeout, cancellation and overload behavior.

### 14.2 Adapter contract tests

Every adapter must pass the same contract suite:

- Valid input shape/layout and color order.
- Deterministic preprocessing configuration.
- Output parsing for empty and non-empty detections.
- Coordinate restoration to original-image pixels.
- Invalid/non-finite output rejection.
- Model metadata and label-map consistency.
- Runtime errors mapped to stable internal errors.
- Resource cleanup and repeated load/close behavior.

### 14.3 Integration and hardware tests

- Use a pinned, licensed test model artifact acquired outside Git.
- Verify artifact checksum and model/runtime compatibility.
- Test representative images with known expected classes and approximate boxes.
- Test CPU and each claimed accelerator provider separately.
- Measure cold start, warm-up, p50/p95/p99 latency, throughput, peak RAM/VRAM and behavior under concurrent load.
- Keep hardware-specific tests labeled and separate from deterministic CI unit tests.
- CI must not silently download large weights or require an unconfigured GPU.

### 14.4 Quality evaluation

A model is not accepted based only on “it runs.” Evaluate on a versioned representative dataset with documented annotation quality and metrics appropriate to the task, such as precision, recall, mAP at stated IoU thresholds, per-class performance and false-positive/false-negative review.

Acceptance thresholds are product decisions and must be written before model promotion. Do not invent accuracy claims or use an unrepresentative sample as a production guarantee.

## 15. Performance and release acceptance criteria

A detection release is acceptable only when all applicable criteria have evidence:

1. Public API and response schema are documented and contract-tested.
2. Existing image-analysis endpoint remains backward-compatible.
3. At least one concrete adapter is selected through hardware/runtime compatibility and license review.
4. Model artifact provenance, checksum, label map, preprocessing and runtime versions are pinned.
5. Model lifecycle, readiness, warm-up, draining and cleanup are tested.
6. All resource controls are configurable, bounded and tested at boundaries.
7. Inference cannot block the ASGI event loop.
8. Overload, timeout, model-not-ready, invalid-output and runtime-failure paths are covered.
9. Adapter contract suite passes.
10. Representative quality and hardware performance reports exist.
11. Logs/metrics support diagnosing model load and inference failures without leaking sensitive data.
12. Frontend distinguishes empty results from failures and renders boxes in the correct coordinate system.
13. CI passes on the exact PR head; docs and deployment configuration are reviewed.
14. Rollback to the previous model version is documented and rehearsed.

No numeric latency, throughput or accuracy SLO is set here because target hardware, workload and acceptance dataset have not yet been supplied. These values must be agreed and measured before production sign-off.

## 16. Delivery plan and decision gates

### Detection Phase A — Contract and benchmark preparation

- Inspect the actual domain detector contract and current package layout.
- Finalize request/response schemas and coordinate/color/tensor conventions.
- Obtain target hardware and workload profile.
- Shortlist model artifacts based on object taxonomy, license, artifact format and runtime compatibility.
- Build a reproducible benchmark harness and representative evaluation dataset.
- **Exit:** reviewed contract, candidate matrix, license review and benchmark plan.

### Detection Phase B — First concrete adapter

- Implement one runtime adapter behind the detector port.
- Implement strict manifest and artifact verification.
- Implement preprocessing, output parsing, coordinate restoration and result validation.
- Add lifecycle manager and bounded inference admission.
- **Exit:** adapter contract suite and CPU/hardware integration evidence pass.

### Detection Phase C — API and frontend integration

- Add POST /api/v1/detections without changing the existing image-analysis endpoint.
- Add response schemas, error mapping and API contract tests.
- Add result overlay and empty/error/loading states to the web client.
- **Exit:** end-to-end tests and UI contract validation pass.

### Detection Phase D — Production readiness

- Add required metrics/logging, deployment resource controls, health/readiness semantics and operational runbook.
- Run load, failure and rollback tests on the target deployment profile.
- **Exit:** documented SLOs met on target hardware and release checklist approved.

Additional runtime adapters, asynchronous jobs, batch processing, video and tracking should be planned only after the first adapter has real usage and benchmark evidence.

## 17. Open decisions — must not be guessed

The following inputs are required before selecting a production model/runtime or publishing performance targets:

- Deployment OS and exact CPU/GPU model(s).
- RAM and accelerator memory available to the service.
- Expected image dimensions and formats.
- Expected concurrency and peak request rate.
- Required object classes/taxonomy and acceptable false-positive/false-negative trade-off.
- Latency and throughput targets.
- Model licensing and intended commercial/distribution context.
- Whether the first deployment is CPU-only, accelerator-enabled or must support both.

Until these are supplied and evaluated, keep the architecture runtime-neutral and do not claim a specific model/runtime as selected.

## 18. Explicit implementation status

As of this document's approval:

- The repository has a basic image-analysis vertical slice and hardened image ingestion.
- Domain-level processing and object-detector contracts exist.
- A concrete object-detection inference adapter, model artifact, registry, lifecycle manager, detection API and real detection UI are **not implemented by this architecture document**.
- All API shapes and package paths above are target contracts/design guidance until implemented and tested.

This document is the design authority for the first object-detection capability. Any deviation must be recorded with its rationale, compatibility impact, security/resource implications and updated acceptance criteria.
