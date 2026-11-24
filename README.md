# VisionAI Platform

A modular computer-vision platform built with Python, FastAPI, OpenCV and React. The repository currently delivers a hardened image-analysis vertical slice and a layered backend foundation with explicit application ports and infrastructure adapters.

## Engineering governance

- [AGENTS.md](AGENTS.md): mandatory repository rules.
- [Master engineering prompt](docs/MASTER_PROMPT.md)
- [Architecture overview](docs/architecture/overview.md)
- [Object Detection Engine architecture](docs/architecture/object-detection-engine.md)
- [Detection Phase A assessment](docs/research/detection-phase-a-assessment.md)
- [Roadmap](docs/roadmap.md)

All changes must be evidence-based, tested, documented and delivered through an independent branch and pull request. Do not commit directly to main.

## Implemented

- FastAPI application, versioned image-analysis API and liveness endpoint.
- JPEG, PNG and WebP format verification, upload-byte limit, decoded dimension/pixel limits.
- Pillow/OpenCV infrastructure adapter with explicit BGR image-frame semantics.
- Application use case and ports separated from the concrete OpenCV implementation.
- Basic image metrics: dimensions, grayscale mean, Laplacian sharpness and 16-bin BGR histograms.
- React/TypeScript/Vite client for upload, preview and analysis-result visualization.
- Unit, API and architecture-boundary tests.
- CI backend matrix for Python 3.10 and 3.12, plus frontend production build.

## Not implemented

Concrete object-detection inference, model artifacts, model lifecycle/readiness, segmentation, tracking, OCR, video/camera processing, authentication, persistence, job queues, multi-tenancy, production observability and deployment profiles are not implemented. Domain protocols and architecture documents are not executable model capabilities.

No production model/runtime is selected. See the Phase A assessment for the remaining hardware, taxonomy, workload, dataset and licensing gates. No model weights are stored in Git.

## Requirements

Python 3.10+ and Node.js 20+.

## Backend setup

From the repository root:

```bash
python -m venv .venv
# Windows CMD: .venv\\Scripts\\activate.bat
# PowerShell: .venv\\Scripts\\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "backend[dev]"
uvicorn visionai.main:app --app-dir backend/src --reload
```

API documentation: http://127.0.0.1:8000/docs

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The default API base URL is http://127.0.0.1:8000. Override it with VITE_API_BASE_URL in frontend/.env.local.

## Validation

From repository root:

```bash
pytest
ruff check backend/src tests
```

Frontend production build:

```bash
cd frontend
npm run build
```

## Configuration

Copy backend/.env.example to backend/.env and adjust VISIONAI_* settings. Defaults cap uploads at 10 MiB, width/height at 8000 px and total pixels at 12,000,000. Application-level controls do not replace reverse-proxy request-body limits or deployment-wide concurrency controls.

No license has been selected. Until one is explicitly added, treat this repository as all-rights-reserved.
