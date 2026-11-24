import cv2
import numpy as np
import pytest
from visionai.services.image_analysis import (
    ImageLimitExceededError,
    analyze_image,
    decode_image,
)


def encode_png(width: int, height: int) -> bytes:
    source = np.zeros((height, width, 3), dtype=np.uint8)
    success, encoded = cv2.imencode(".png", source)
    assert success
    return encoded.tobytes()


def test_decode_image_returns_bgr_array() -> None:
    decoded = decode_image(encode_png(16, 12))
    assert decoded is not None
    assert decoded.shape == (12, 16, 3)


def test_decode_image_rejects_invalid_bytes() -> None:
    assert decode_image(b"not-an-image") is None


def test_decode_image_rejects_declared_mime_mismatch() -> None:
    assert decode_image(
        encode_png(16, 12), expected_mime_type="image/jpeg"
    ) is None


def test_decode_image_rejects_unsupported_format() -> None:
    assert decode_image(encode_png(16, 12), expected_mime_type="image/gif") is None


def test_decode_image_enforces_maximum_width_before_decode() -> None:
    with pytest.raises(ImageLimitExceededError, match="configured processing limits"):
        decode_image(encode_png(16, 12), max_width=15)


def test_decode_image_enforces_maximum_height_before_decode() -> None:
    with pytest.raises(ImageLimitExceededError, match="configured processing limits"):
        decode_image(encode_png(16, 12), max_height=11)


def test_decode_image_enforces_total_pixel_limit() -> None:
    with pytest.raises(ImageLimitExceededError, match="configured processing limits"):
        decode_image(encode_png(16, 12), max_pixels=191)


def test_decode_image_accepts_image_at_exact_pixel_limit() -> None:
    decoded = decode_image(encode_png(16, 12), max_pixels=192)
    assert decoded is not None
    assert decoded.shape == (12, 16, 3)


def test_analyze_image_returns_dimensions_and_histograms() -> None:
    result = analyze_image(np.zeros((10, 20, 3), dtype=np.uint8))
    assert (result["width"], result["height"], result["channels"]) == (20, 10, 3)
    assert set(result["histogram"]) == {"blue", "green", "red"}
    assert all(len(bins) == 16 for bins in result["histogram"].values())


def test_analyze_image_rejects_invalid_shape() -> None:
    with pytest.raises(ValueError):
        analyze_image(np.zeros((10, 10), dtype=np.uint8))
