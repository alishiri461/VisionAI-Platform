from io import BytesIO

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError


class ImageLimitExceededError(ValueError):
    """Raised when decoded image dimensions exceed configured resource limits."""


_MIME_FORMATS = {
    "image/jpeg": "JPEG",
    "image/png": "PNG",
    "image/webp": "WEBP",
}


def decode_image(
    content: bytes,
    *,
    max_width: int = 8000,
    max_height: int = 8000,
    max_pixels: int = 12_000_000,
    expected_mime_type: str | None = None,
) -> np.ndarray | None:
    """Validate image headers and resource bounds before decoding to a BGR array.

    Returns None for malformed, unsupported, or MIME-mismatched content. Raises
    ImageLimitExceededError when the declared dimensions exceed configured limits.
    """
    if not content:
        return None

    try:
        with Image.open(BytesIO(content)) as source:
            image_format = source.format
            width, height = source.size
            if image_format not in {"JPEG", "PNG", "WEBP"}:
                return None
            if expected_mime_type is not None:
                expected_format = _MIME_FORMATS.get(expected_mime_type)
                if expected_format != image_format:
                    return None
            if width <= 0 or height <= 0:
                return None
            if width > max_width or height > max_height or width * height > max_pixels:
                raise ImageLimitExceededError(
                    "Image dimensions exceed configured processing limits."
                )
            source.verify()
    except ImageLimitExceededError:
        raise
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError, Image.DecompressionBombError):
        return None

    encoded = np.frombuffer(content, dtype=np.uint8)
    image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if image is None or image.size == 0:
        return None

    decoded_height, decoded_width = image.shape[:2]
    if (
        decoded_width != width
        or decoded_height != height
        or decoded_width > max_width
        or decoded_height > max_height
        or decoded_width * decoded_height > max_pixels
    ):
        raise ImageLimitExceededError(
            "Decoded image dimensions exceed configured processing limits."
        )
    return image


def analyze_image(image: np.ndarray) -> dict:
    """Calculate basic, deterministic image quality and color statistics."""
    if image.ndim != 3 or image.shape[2] != 3 or image.size == 0:
        raise ValueError("Expected a non-empty 3-channel BGR image.")
    height, width, channels = image.shape
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    histogram = {}
    for index, name in enumerate(("blue", "green", "red")):
        bins = cv2.calcHist([image], [index], None, [16], [0, 256])
        histogram[name] = [int(value) for value in bins.flatten()]
    laplacian = cv2.Laplacian(gray, cv2.CV_32F)
    return {
        "width": int(width), "height": int(height), "channels": int(channels),
        "mean_grayscale": round(float(gray.mean()), 4),
        "sharpness_laplacian_variance": round(float(laplacian.var()), 4),
        "histogram": histogram,
    }
