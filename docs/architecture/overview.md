# Architecture Overview

## Architectural style
The implementation is a modular monolith. Image-processing logic remains independent of FastAPI so future workers, CLI tools and transports can reuse it.

## Logical boundaries
- API: HTTP validation, serialization and transport.
- Application: use-case orchestration.
- Processing services: deterministic image operations and inference pipelines.
- Model adapters (planned): stable interfaces around PyTorch and ONNX Runtime.
- Infrastructure (planned): PostgreSQL, Redis, object storage and telemetry.

## Current vertical slice
Browser upload -> bounded upload read -> declared MIME allow-list -> Pillow header/format inspection and dimension preflight -> OpenCV decode -> deterministic image metrics -> JSON response -> browser rendering.

## Image resource controls
- Upload bytes are capped by VISIONAI_MAX_UPLOAD_BYTES (default 10 MiB).
- Decoded width and height are capped independently by VISIONAI_MAX_IMAGE_WIDTH and VISIONAI_MAX_IMAGE_HEIGHT (defaults 8000 each).
- Total decoded pixels are capped by VISIONAI_MAX_IMAGE_PIXELS (default 12,000,000).
- The actual encoded format must match the declared JPEG/PNG/WebP media type.
- Image decode and analysis execute off the event loop, with at most two in-flight image processing operations per application process.
- Laplacian intermediate precision uses float32 to reduce temporary memory versus float64.

These are configurable application-level limits. Reverse-proxy/server request limits and deployment-wide concurrency limits must also be configured for a production deployment.

## Real-time boundary
WebSocket is intended for session control and metadata. WebRTC or another media transport is required for browser video; raw video frames should not be sent through an unbounded WebSocket queue.

## Security
Treat uploads as untrusted. Validate declared media type, inspect actual format, enforce byte and decoded-pixel/dimension limits before OpenCV allocation, and return stable errors. Do not trust filenames or persist uploads without an explicit storage and tenant-isolation design. Treat imported model files as untrusted artifacts.
