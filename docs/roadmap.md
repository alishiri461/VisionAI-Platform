# Delivery Roadmap

This roadmap tracks intended delivery, not a claim that every listed capability exists. The canonical engineering rules and phase exit criteria are in [MASTER_PROMPT.md](MASTER_PROMPT.md).

| Phase | Scope | Status | Exit evidence |
|---|---|---|---|
| 0 | Repository foundation, architecture, engineering instructions and contracts | Initial foundation added | Reviewed architecture/contracts, documented constraints, CI baseline |
| 1 | API/web vertical slice, upload and basic image analysis | Implemented initial slice; CI green on recorded PR head | Backend tests, Ruff, frontend production build |
| 2 | Harden image ingestion, decoded dimensions/pixel limits, expanded OpenCV operations and export | Image byte/dimension/pixel limits and bounded processing concurrency implemented; further deployment-level controls remain | Unit/API boundary tests, malformed media tests, deployment request/concurrency limits |
| 3 | Product-grade object detection capability: model/runtime selection, artifact manifest, lifecycle, bounded inference, stable API and result visualization | Architecture documented and approved; implementation not started; only domain-level contracts exist | Target hardware/workload decision record, licensed immutable model artifact, concrete adapter, lifecycle/readiness tests, detection API contract tests, representative quality and hardware benchmark evidence |
| 4 | Video decoding, batch processing and tracking | Planned | Bounded batch/resource model, video fixtures, deterministic tracking contracts/tests |
| 5 | Camera sessions, bounded frame buffers and real-time transport | Planned | Explicit media transport, backpressure/drop policy, session lifecycle and load evidence |
| 6 | Segmentation, OCR and anomaly detection | Planned | Independent capability contracts, concrete adapters, accuracy/latency evaluation |
| 7 | Authentication, persistence, queue, observability and deployment hardening | Planned | Authorization/tenant tests, durable job semantics, telemetry, deployment/rollback evidence |

## Delivery rules

1. A phase is complete only after acceptance criteria, automated tests, integration evidence where applicable, security review and documentation are satisfied.
2. Code presence alone is not completion evidence. A protocol, placeholder, UI control, or roadmap entry does not make a capability implemented.
3. CI results must be tied to the exact commit SHA. Failed, skipped, cancelled, or unavailable checks must be reported accurately.
4. Do not advance by hiding earlier critical failures or weakening quality gates.
5. Reorder phases only when a documented dependency or explicit product requirement justifies it.

## Immediate next work

1. Verify image ingestion boundary tests and CI against the current PR head.
2. Add reverse-proxy/server request-body limits and deployment-wide concurrency controls in the chosen deployment profile.
3. Add observability for rejected uploads, processing wait time, decode failures, and processing latency.
4. Execute Detection Phase A in [Object Detection Engine architecture](architecture/object-detection-engine.md): inspect the existing detector port, collect target hardware/workload/object-taxonomy requirements, complete model/license evaluation, and prepare a reproducible benchmark before selecting a runtime or implementing inference.
