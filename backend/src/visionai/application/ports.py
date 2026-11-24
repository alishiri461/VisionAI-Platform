"""Ports required by application use cases."""
from typing import Protocol

from visionai.domain.image import ImageFrame


class ImageDecoder(Protocol):
    def decode(
        self, content: bytes, *, max_width: int, max_height: int,
        max_pixels: int, expected_mime_type: str,
    ) -> ImageFrame | None:
        ...


class ImageAnalyzer(Protocol):
    def analyze(self, image: ImageFrame) -> dict[str, object]:
        ...
