# Architecture Overview

## Architectural style

VisionAI is a **modular monolith**. The backend separates domain contracts, application orchestration, infrastructure adapters and HTTP presentation. This provides explicit boundaries without introducing distributed-service complexity before workload evidence requires it.

## Dependency direction

```text
HTTP Presentation -> Application Use Cases -> Domain Contracts
                           |
                           v
                    Application Ports
                           ^
                           |
                Infrastructure Adapters
```

- **Domain:** framework-neutral value objects and business contracts. It must not import FastAPI, OpenCV, NumPy, Pillow, PyTorch or ONNX Runtime.
- **Application:** use-case orchestration and ports. It must not import HTTP frameworks or concrete infrastructure adapters.
- **Infrastructure:** concrete implementations for image decoding, CV runtimes, persistence and external systems.
- **Presentation:** HTTP validation, request limits, response serialization and transport-specific error mapping.
- **Frontend:** feature-oriented React UI; it communicates only through versioned API contracts.

## Current image-analysis flow

Browser upload -> FastAPI multipart boundary -> bounded byte read -> declared MIME allow-list -> application use case -> OpenCV/Pillow decoder adapter -> immutable ImageFrame with explicit BGR semantics -> analyzer adapter -> response schema -> browser visualization.

The existing public endpoint remains POST /api/v1/images/analyze. The use case is runtime-neutral; OpenCV/Pillow are implementation details in infrastructure.

## Resource controls

- Upload bytes: VISIONAI_MAX_UPLOAD_BYTES (default 10 MiB).
- Width and height: VISIONAI_MAX_IMAGE_WIDTH and VISIONAI_MAX_IMAGE_HEIGHT (default 8000 each).
- Total decoded pixels: VISIONAI_MAX_IMAGE_PIXELS (default 12,000,000).
- Image processing admission: at most two in-flight decode/analysis operations per application process.
- CPU-bound decode and analysis execute outside the async event loop.

These are application-process controls. Configure request-body limits at the reverse proxy/ASGI ingress and deployment-wide concurrency controls before public exposure.

## Object Detection Engine

The product-level design authority is [Object Detection Engine — Product Architecture](object-detection-engine.md). The target detection capability is model/runtime-neutral: application and API code depend on stable contracts; concrete PyTorch, ONNX Runtime, OpenVINO or TensorRT adapters remain infrastructure concerns.

The initial endpoint target is POST /api/v1/detections and must reuse the hardened image-ingestion boundary without changing the existing image-analysis contract. A production model/runtime has not been selected. Hardware, workload, object taxonomy, dataset rights, quality targets and deployment/license posture must pass the Phase A decision gates before concrete inference is implemented.

## Real-time boundary

WebSocket is for session control and metadata, not an unbounded raw-frame transport. Browser video requires a deliberate media transport (for example WebRTC), bounded frame buffers, explicit backpressure/drop policy and session lifecycle.

## Security

Uploads are untrusted. Validate actual file format, declared MIME type, byte size and decoded dimensions before allocating image buffers. Do not trust filenames. Do not load arbitrary model URLs, Python pickles or user-supplied executable code. Model artifacts require provenance and SHA-256 verification. Persistence, authentication, tenant isolation and retention require explicit decisions before enabling storage of user images.
