import cv2
import numpy as np


def decode_image(content: bytes) -> np.ndarray | None:
    """Decode untrusted image bytes into a BGR image."""
    if not content:
        return None
    image = cv2.imdecode(np.frombuffer(content, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None or image.size == 0:
        return None
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
    return {
        "width": int(width), "height": int(height), "channels": int(channels),
        "mean_grayscale": round(float(gray.mean()), 4),
        "sharpness_laplacian_variance": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 4),
        "histogram": histogram,
    }
