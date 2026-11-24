import cv2
import numpy as np
import pytest
from visionai.services.image_analysis import analyze_image, decode_image


def test_decode_image_returns_bgr_array() -> None:
    source = np.zeros((12, 16, 3), dtype=np.uint8)
    success, encoded = cv2.imencode(".png", source)
    assert success
    decoded = decode_image(encoded.tobytes())
    assert decoded is not None
    assert decoded.shape == (12, 16, 3)


def test_decode_image_rejects_invalid_bytes() -> None:
    assert decode_image(b"not-an-image") is None


def test_analyze_image_returns_dimensions_and_histograms() -> None:
    result = analyze_image(np.zeros((10, 20, 3), dtype=np.uint8))
    assert (result["width"], result["height"], result["channels"]) == (20, 10, 3)
    assert set(result["histogram"]) == {"blue", "green", "red"}
    assert all(len(bins) == 16 for bins in result["histogram"].values())


def test_analyze_image_rejects_invalid_shape() -> None:
    with pytest.raises(ValueError):
        analyze_image(np.zeros((10, 10), dtype=np.uint8))
