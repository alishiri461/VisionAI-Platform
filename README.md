# VisionAI Platform

A modular computer-vision web platform built with Python, FastAPI, OpenCV and React. This repository starts with a working-scope foundation: image upload, safe decoding, basic image metrics and a browser client.

## Current implementation

- FastAPI application with versioned routes and liveness endpoint.
- JPEG/PNG/WebP upload validation and configured byte-size limit.
- OpenCV decoding and basic image metrics (dimensions, grayscale mean, Laplacian sharpness and color histograms).
- React + TypeScript + Vite client.
- Unit tests for image-processing functions.
- Architecture overview and phased roadmap.

Object detection, tracking, segmentation, OCR, video analytics, camera streaming, authentication, persistence, queues and production monitoring are **not implemented yet**.

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

## Tests

```bash
pytest
```

Configuration examples: `backend/.env.example` and `frontend/.env.example`.

No license has been selected. Until one is added, treat the repository as all-rights-reserved.
