import cv2
import numpy as np
from fastapi.testclient import TestClient
from visionai.api.v1.routes import images as image_routes
from visionai.core.config import Settings
from visionai.main import app


def make_png(width: int = 16, height: int = 12) -> bytes:
    pixels = np.zeros((height, width, 3), dtype=np.uint8)
    success, encoded = cv2.imencode(".png", pixels)
    assert success
    return encoded.tobytes()


def test_image_api_returns_analysis_for_valid_png(monkeypatch) -> None:
    settings = Settings()
    monkeypatch.setattr(image_routes, "get_settings", lambda: settings)
    response = TestClient(app).post(
        "/api/v1/images/analyze",
        files={"file": ("sample.png", make_png(), "image/png")},
    )
    assert response.status_code == 200
    assert response.json()["width"] == 16
    assert response.json()["height"] == 12


def test_image_api_rejects_mime_content_mismatch(monkeypatch) -> None:
    monkeypatch.setattr(image_routes, "get_settings", Settings)
    response = TestClient(app).post(
        "/api/v1/images/analyze",
        files={"file": ("sample.jpg", make_png(), "image/jpeg")},
    )
    assert response.status_code == 422


def test_image_api_rejects_decoded_dimensions_over_limit(monkeypatch) -> None:
    settings = Settings(max_image_width=10)
    monkeypatch.setattr(image_routes, "get_settings", lambda: settings)
    response = TestClient(app).post(
        "/api/v1/images/analyze",
        files={"file": ("sample.png", make_png(), "image/png")},
    )
    assert response.status_code == 413


def test_image_api_rejects_malformed_image_bytes(monkeypatch) -> None:
    monkeypatch.setattr(image_routes, "get_settings", Settings)
    response = TestClient(app).post(
        "/api/v1/images/analyze",
        files={"file": ("broken.png", b"not-a-valid-image", "image/png")},
    )
    assert response.status_code == 422


def test_image_api_rejects_unsupported_declared_media_type(monkeypatch) -> None:
    monkeypatch.setattr(image_routes, "get_settings", Settings)
    response = TestClient(app).post(
        "/api/v1/images/analyze",
        files={"file": ("sample.gif", make_png(), "image/gif")},
    )
    assert response.status_code == 415


def test_image_api_enforces_upload_byte_limit(monkeypatch) -> None:
    settings = Settings(max_upload_bytes=1024)
    monkeypatch.setattr(image_routes, "get_settings", lambda: settings)
    rng = np.random.default_rng(42)
    pixels = rng.integers(0, 256, (128, 128, 3), dtype=np.uint8)
    success, encoded = cv2.imencode(".png", pixels)
    assert success and len(encoded) > settings.max_upload_bytes
    response = TestClient(app).post(
        "/api/v1/images/analyze",
        files={"file": ("large.png", encoded.tobytes(), "image/png")},
    )
    assert response.status_code == 413
