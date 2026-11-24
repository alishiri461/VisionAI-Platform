# Delivery Roadmap

This roadmap distinguishes implemented behavior from planned capability. A protocol, architecture document or UI placeholder is not an implemented feature.

| Phase | Scope | Status | Exit evidence |
|---|---|---|---|
| 0 | Repository foundation, modular boundaries, engineering rules and CI | Foundation implemented; continuing hardening | Architecture tests, CI on supported Python versions, reviewed contracts |
| 1 | Image upload and basic image analysis vertical slice | Implemented | Unit/API tests, backend lint, frontend production build |
| 2 | Image ingestion hardening and operational limits | Application byte/dimension/pixel limits implemented; ingress controls still required | Boundary and malformed-image tests, reverse-proxy request limit, deployment concurrency policy |
| 3 | Object detection: model selection, artifact manifest, lifecycle, bounded inference, API and result visualization | Architecture and Phase A assessment documented; concrete inference not implemented | Approved taxonomy/dataset, target workload/hardware, artifact provenance/license, benchmark, selection ADR, adapter/API/UI tests |
| 4 | Video decoding, batch processing and object tracking | Planned | Bounded batch/resource design, video fixtures and deterministic tracking tests |
| 5 | Camera sessions and real-time media transport | Planned | Explicit media transport, bounded frame buffers, backpressure and session lifecycle tests |
| 6 | Segmentation, OCR and anomaly detection | Planned | Independent contracts, concrete adapters and task-specific evaluation |
| 7 | Authentication, persistence, job queue, observability and deployment hardening | Planned | Authorization/tenant tests, durable job semantics, telemetry, deployment and rollback evidence |

## Delivery rules

1. A phase is complete only when acceptance criteria, automated tests, integration evidence, security review and documentation are satisfied.
2. Do not claim a model/runtime, dataset, benchmark, endpoint or deployment exists without its artifact and test evidence.
3. CI results must be tied to the exact commit SHA.
4. Do not weaken tests or lint to make CI green.
5. Do not introduce a database, queue, authentication provider or microservice without a documented requirement and decision record.

## Immediate next decisions

1. Confirm whether the supplied RTX 3060 Ti workstation is a development/benchmark machine or final production host.
2. Provide object taxonomy, image dimensions, concurrency, throughput, latency and per-class quality targets.
3. Approve evaluation dataset provenance and intended licensing/deployment posture.
4. Complete the official runtime compatibility matrix for Windows, Python, CUDA and cuDNN before installing GPU packages.
5. Run the model/runtime benchmark and approve a selection ADR before implementing inference.
6. Define deployment ingress/body limits, process-wide concurrency and telemetry before exposing the API publicly.
