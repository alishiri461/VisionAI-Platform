# Architecture Overview

## Architectural style
The initial implementation is a modular monolith. Image-processing logic must remain independent of FastAPI so future workers, CLI tools and transports can reuse it.

## Logical boundaries
- API: HTTP validation, serialization and transport.
- Application: use-case orchestration.
- Processing services: deterministic image operations and inference pipelines.
- Model adapters (planned): stable interfaces around PyTorch and ONNX Runtime.
- Infrastructure (planned): PostgreSQL, Redis, object storage and telemetry.

## Current vertical slice
Browser upload -> FastAPI validation -> bounded byte read -> OpenCV decode -> image metrics -> JSON response -> browser rendering.

## Real-time boundary
WebSocket is intended for session control and metadata. WebRTC or another media transport is required for browser video; raw video frames should not be sent through an unbounded WebSocket queue.

## Security
Enforce upload size and accepted media types; decode bytes rather than trusting filenames; add decoded pixel/dimension limits before public deployment; isolate persisted uploads by user/tenant; treat imported model files as untrusted artifacts.
