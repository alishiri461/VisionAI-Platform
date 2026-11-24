"""Image-analysis orchestration independent from FastAPI and CV libraries."""
from dataclasses import dataclass

from visionai.application.ports import ImageAnalyzer, ImageDecoder


class InvalidImageContentError(ValueError):
    """The payload is not a supported image matching its declared media type."""


class ImageLimitExceededError(ValueError):
    """Decoded image dimensions exceed the configured resource limits."""


@dataclass(frozen=True, slots=True)
class AnalyzeImageUseCase:
    decoder: ImageDecoder
    analyzer: ImageAnalyzer

    def execute(
        self, content: bytes, *, content_type: str, max_width: int,
        max_height: int, max_pixels: int,
    ) -> dict[str, object]:
        frame = self.decoder.decode(
            content, max_width=max_width, max_height=max_height,
            max_pixels=max_pixels, expected_mime_type=content_type,
        )
        if frame is None:
            raise InvalidImageContentError(
                "Uploaded content is not a valid image matching its declared media type."
            )
        return self.analyzer.analyze(frame)
