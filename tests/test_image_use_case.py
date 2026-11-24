from dataclasses import dataclass

import pytest
from visionai.application.use_cases.analyze_image import (
    AnalyzeImageUseCase,
    InvalidImageContentError,
)
from visionai.domain.image import ColorOrder, ImageFrame


@dataclass
class FakeDecoder:
    frame: ImageFrame | None
    calls: list[dict[str, object]]

    def decode(self, content: bytes, **kwargs: object) -> ImageFrame | None:
        self.calls.append({"content": content, **kwargs})
        return self.frame


@dataclass
class FakeAnalyzer:
    result: dict[str, object]
    received: list[ImageFrame]

    def analyze(self, image: ImageFrame) -> dict[str, object]:
        self.received.append(image)
        return self.result


def test_use_case_coordinates_decoder_and_analyzer() -> None:
    frame = ImageFrame(object(), 10, 8, 3, ColorOrder.BGR)
    expected = {"width": 10, "height": 8}
    decoder = FakeDecoder(frame, [])
    analyzer = FakeAnalyzer(expected, [])
    result = AnalyzeImageUseCase(decoder, analyzer).execute(
        b"image", content_type="image/png", max_width=100,
        max_height=100, max_pixels=10_000,
    )
    assert result == expected
    assert analyzer.received == [frame]
    assert decoder.calls == [{
        "content": b"image", "max_width": 100, "max_height": 100,
        "max_pixels": 10_000, "expected_mime_type": "image/png",
    }]


def test_invalid_image_never_reaches_analyzer() -> None:
    decoder = FakeDecoder(None, [])
    analyzer = FakeAnalyzer({}, [])
    use_case = AnalyzeImageUseCase(decoder, analyzer)
    with pytest.raises(InvalidImageContentError):
        use_case.execute(
            b"invalid", content_type="image/png", max_width=100,
            max_height=100, max_pixels=10_000,
        )
    assert analyzer.received == []
