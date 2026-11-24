from fastapi import APIRouter, File, HTTPException, UploadFile, status

from visionai.core.config import get_settings
from visionai.schemas.image import ImageAnalysisResponse
from visionai.services.image_analysis import analyze_image, decode_image

router = APIRouter()
_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/analyze", response_model=ImageAnalysisResponse)
async def analyze_uploaded_image(file: UploadFile = File(...)) -> ImageAnalysisResponse:
    settings = get_settings()
    if file.content_type not in _ALLOWED_TYPES:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                            "Allowed image types: JPEG, PNG and WebP.")
    content = await file.read(settings.max_upload_bytes + 1)
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            "Image exceeds configured upload limit.")
    image = decode_image(content)
    if image is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "Uploaded content is not a decodable image.")
    try:
        return ImageAnalysisResponse(**analyze_image(image))
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
