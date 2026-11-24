# VisionAI Platform

A modular computer-vision web platform built with Python, FastAPI, OpenCV and React. The current repository provides an initial foundation and image-analysis vertical slice: image upload, safe decoding, deterministic basic metrics and a browser client.

## Project governance

- Canonical engineering instructions: [AGENTS.md](AGENTS.md)
- Master engineering prompt: [docs/MASTER_PROMPT.md](docs/MASTER_PROMPT.md)
- Architecture: [docs/architecture/overview.md](docs/architecture/overview.md)
- Object Detection Engine product architecture: [docs/architecture/object-detection-engine.md](docs/architecture/object-detection-engine.md)
- Detection Phase A technical assessment and benchmark plan: [docs/research/detection-phase-a-assessment.md](docs/research/detection-phase-a-assessment.md)
- Delivery roadmap: [docs/roadmap.md](docs/roadmap.md)

All work must follow the master prompt's evidence-based workflow, branch protections, security/resource limits, quality gates, and definition of done.

## Current implementation

- FastAPI application with versioned routes and liveness endpoint.
- JPEG/PNG/WebP upload validation and configured byte-size limit.
- OpenCV decoding and basic image metrics (dimensions, grayscale mean, Laplacian sharpness and color histograms).
- React + TypeScript + Vite client.
- Unit tests for image-processing functions.
- Domain contracts for pluggable processing and object detection; these are interfaces, not concrete inference implementations.
- Architecture overview, roadmap, and CI workflow.

Object detection inference, tracking, segmentation, OCR, video analytics, camera streaming, authentication, persistence, queues and production monitoring are **not implemented yet**.

## Requirements

Python 3.12+, Node.js 20+, npm.

## Backend

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e "backend[dev]"
uvicorn visionai.main:app --app-dir backend/src --reload
```

API docs: http://127.0.0.1:8000/docs

## Frontend

```bash
cd frontend
npm install
npm run dev
```

The client defaults to http://127.0.0.1:8000. Set `VITE_API_BASE_URL` in `frontend/.env.local` to override it.

## Tests and quality checks

```bash
pytest
ruff check backend/src tests
```

Frontend production build:

```bash
cd frontend
npm run build
```

Configuration examples: `backend/.env.example` and `frontend/.env.example`. Image limits default to 8000 px per dimension and 12,000,000 total pixels; override with `VISIONAI_MAX_IMAGE_WIDTH`, `VISIONAI_MAX_IMAGE_HEIGHT`, and `VISIONAI_MAX_IMAGE_PIXELS`.

No license has been selected. Until one is added, treat the repository as all-rights-reserved.
