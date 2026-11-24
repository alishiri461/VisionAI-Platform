from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from visionai.api.v1.router import api_router
from visionai.core.config import get_settings

settings = get_settings()
app = FastAPI(title="VisionAI Platform API", version="0.1.0",
              description="Modular computer-vision platform API.")
app.add_middleware(
    CORSMiddleware, allow_origins=settings.allowed_origins,
    allow_credentials=False, allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health/live", tags=["health"])
def liveness() -> dict[str, str]:
    return {"status": "alive"}
