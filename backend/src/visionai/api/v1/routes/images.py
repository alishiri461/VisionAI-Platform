import asyncio
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from starlette.concurrency import run_in_threadpool

from visionai.application.use_cases.analyze_image import (
    ImageLimitExceededError,
    InvalidImageContentError,
)
from visionai.bootstrap import build_image_analysis_use_case
from visionai.core.config import Settings, get_settings
from visionai.schemas.image import ImageAnalysisResponse

router = APIRouter()
_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
_IMAGE_PROCESSING_SEMAPHORE = asyncio.Semaphore(2)
_USE_CASE = build_image_analysis_use_case()


def _execute_analysis(content: bytes, settings: Settings, content_type: str) -> ImageAnalysisResponse:
    result = _USE_CASE.execute(
        content, content_type=content_type,
        max_width=settings.max_image_width,
        max_height=settings.max_image_height,
        max_pixels=settings.max_image_pixels,
    )
    return ImageAnalysisResponse(**result)


@router.post("/analyze", response_model=ImageAnalysisResponse)
async def analyze_uploaded_image(file: Annotated[UploadFile, File()]) -> ImageAnalysisResponse:
    settings = get_settings()
    content_type = file.content_type or ""
    if content_type not in _ALLOWED_TYPES:
        await file.close()
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "Allowed image types: JPEG, PNG and WebP.",
        )

    async with _IMAGE_PROCESSING_SEMAPHORE:
        try:
            content = await file.read(settings.max_upload_bytes + 1)
        finally:
            await file.close()
        if len(content) > settings.max_upload_bytes:
            raise HTTPException(
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                "Image exceeds configured upload byte limit.",
            )
        try:
            return await run_in_threadpool(_execute_analysis, content, settings, content_type)
        except ImageLimitExceededError as exc:
            raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, str(exc)) from exc
        except InvalidImageContentError as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
