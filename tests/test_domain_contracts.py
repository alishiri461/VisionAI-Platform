import math

import pytest

from visionai.domain.detection import Detection
from visionai.domain.image import ColorOrder, ImageFrame


def test_image_frame_rejects_non_positive_dimensions() -> None:
    with pytest.raises(ValueError, match="positive"):
        ImageFrame(object(), 0, 10, 3, ColorOrder.BGR)


def test_image_frame_rejects_unsupported_channel_count() -> None:
    with pytest.raises(ValueError, match="channel"):
        ImageFrame(object(), 10, 10, 2, ColorOrder.BGR)


@pytest.mark.parametrize("confidence", [-0.1, 1.1, math.nan, math.inf])
def test_detection_rejects_invalid_confidence(confidence: float) -> None:
    with pytest.raises(ValueError, match="confidence"):
        Detection("person", confidence, 0, 0, 10, 10)


def test_detection_rejects_inverted_box() -> None:
    with pytest.raises(ValueError, match="non-negative box"):
        Detection("person", 0.9, 10, 0, 2, 8)
