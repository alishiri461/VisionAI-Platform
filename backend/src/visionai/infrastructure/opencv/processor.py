"""Pillow/OpenCV implementation of image decoding and basic analysis."""
from io import BytesIO

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError

from visionai.application.use_cases.analyze_image import ImageLimitExceededError
from visionai.domain.image import ColorOrder, ImageFrame

_MIME_FORMATS = {"image/jpeg": "JPEG", "image/png": "PNG", "image/webp": "WEBP"}


class OpenCvImageProcessor:
    """Stateless infrastructure adapter; no model/runtime is loaded here."""

    def decode(
        self, content: bytes, *, max_width: int, max_height: int,
        max_pixels: int, expected_mime_type: str,
    ) -> ImageFrame | None:
        if not content:
            return None
        try:
            with Image.open(BytesIO(content)) as source:
                image_format = source.format
                width, height = source.size
                if image_format not in {"JPEG", "PNG", "WEBP"}:
                    return None
                if _MIME_FORMATS.get(expected_mime_type) != image_format:
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

        pixels = cv2.imdecode(np.frombuffer(content, dtype=np.uint8), cv2.IMREAD_COLOR)
        if pixels is None or pixels.size == 0:
            return None
        decoded_height, decoded_width = pixels.shape[:2]
        if (
            decoded_width != width or decoded_height != height
            or decoded_width > max_width or decoded_height > max_height
            or decoded_width * decoded_height > max_pixels
        ):
            raise ImageLimitExceededError(
                "Decoded image dimensions exceed configured processing limits."
            )
        return ImageFrame(
            pixels=pixels, width=decoded_width, height=decoded_height,
            channels=3, color_order=ColorOrder.BGR,
        )

    def analyze(self, image: ImageFrame) -> dict[str, object]:
        if image.color_order is not ColorOrder.BGR:
            raise ValueError("OpenCV image analysis requires a BGR image frame.")
        if not isinstance(image.pixels, np.ndarray):
            raise ValueError("Image frame payload must be a NumPy array.")
        pixels = image.pixels
        if pixels.ndim != 3 or pixels.shape[2] != 3 or pixels.size == 0:
            raise ValueError("Expected a non-empty 3-channel BGR image.")
        height, width, channels = pixels.shape
        if (width, height) != (image.width, image.height):
            raise ValueError("Image frame metadata does not match its pixel payload.")
        gray = cv2.cvtColor(pixels, cv2.COLOR_BGR2GRAY)
        histogram: dict[str, list[int]] = {}
        for index, name in enumerate(("blue", "green", "red")):
            bins = cv2.calcHist([pixels], [index], None, [16], [0, 256])
            histogram[name] = [int(value) for value in bins.flatten()]
        laplacian = cv2.Laplacian(gray, cv2.CV_32F)
        return {
            "width": int(width), "height": int(height), "channels": int(channels),
            "mean_grayscale": round(float(gray.mean()), 4),
            "sharpness_laplacian_variance": round(float(laplacian.var()), 4),
            "histogram": histogram,
        }
