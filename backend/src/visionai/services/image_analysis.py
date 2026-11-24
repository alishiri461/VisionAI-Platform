"""Compatibility facade for the initial image-analysis service API."""
from io import BytesIO

import numpy as np
from PIL import Image

from visionai.domain.image import ColorOrder, ImageFrame
from visionai.infrastructure.opencv.processor import ImageLimitExceededError, OpenCvImageProcessor

_processor = OpenCvImageProcessor()


def decode_image(
    content: bytes, *, max_width: int = 8000, max_height: int = 8000,
    max_pixels: int = 12_000_000, expected_mime_type: str | None = None,
) -> np.ndarray | None:
    if expected_mime_type is None:
        try:
            with Image.open(BytesIO(content)) as source:
                expected_mime_type = {
                    "JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp",
                }.get(source.format, "")
        except Exception:
            return None
    frame = _processor.decode(
        content, max_width=max_width, max_height=max_height,
        max_pixels=max_pixels, expected_mime_type=expected_mime_type,
    )
    return None if frame is None else frame.pixels  # type: ignore[return-value]


def analyze_image(image: np.ndarray) -> dict[str, object]:
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Expected a non-empty 3-channel BGR image.")
    height, width, channels = image.shape
    return _processor.analyze(ImageFrame(image, width, height, channels, ColorOrder.BGR))


__all__ = ["ImageLimitExceededError", "analyze_image", "decode_image"]
