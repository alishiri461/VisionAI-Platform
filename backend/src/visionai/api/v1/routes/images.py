import asyncio
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from starlette.concurrency import run_in_threadpool

from visionai.core.config import Settings, get_settings
from visionai.schemas.image import ImageAnalysisResponse
from visionai.services.image_analysis import (
    ImageLimitExceededError,
    analyze_image,
    decode_image,
)

router = APIRouter()
_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
_IMAGE_PROCESSING_SEMAPHORE = asyncio.Semaphore(2)


def _decode_and_analyze(
    content: bytes,
    settings: Settings,
    content_type: str,
) -> ImageAnalysisResponse:
    image = decode_image(
        content,
        max_width=settings.max_image_width,
        max_height=settings.max_image_height,
        max_pixels=settings.max_image_pixels,
        expected_mime_type=content_type,
    )
    if image is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Uploaded content is not a valid image matching its declared media type.",
        )
    return ImageAnalysisResponse(**analyze_image(image))


@router.post("/analyze", response_model=ImageAnalysisResponse)
async def analyze_uploaded_image(
    file: Annotated[UploadFile, File()],
) -> ImageAnalysisResponse:
    settings = get_settings()
    if file.content_type not in _ALLOWED_TYPES:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "Allowed image types: JPEG, PNG and WebP.",
        )

    async with _IMAGE_PROCESSING_SEMAPHORE:
        content = await file.read(settings.max_upload_bytes + 1)
        if len(content) > settings.max_upload_bytes:
            raise HTTPException(
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                "Image exceeds configured upload byte limit.",
            )
        try:
            return await run_in_threadpool(
                _decode_and_analyze, content, settings, file.content_type
            )
        except ImageLimitExceededError as exc:
            raise HTTPException(
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, str(exc)
            ) from exc
        except ValueError as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
