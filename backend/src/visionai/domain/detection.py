"""Framework-neutral object-detection domain contracts."""
from dataclasses import dataclass
from math import isfinite
from typing import Protocol

from visionai.domain.image import ImageFrame


@dataclass(frozen=True, slots=True)
class Detection:
    label: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float
    class_id: int = -1

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise ValueError("Detection label cannot be empty.")
        if not isfinite(self.confidence) or not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Detection confidence must be finite and within [0, 1].")
        coordinates = (self.x1, self.y1, self.x2, self.y2)
        if not all(isfinite(value) for value in coordinates):
            raise ValueError("Detection coordinates must be finite.")
        if self.x2 < self.x1 or self.y2 < self.y1:
            raise ValueError("Detection coordinates must form a non-negative box.")


class ObjectDetector(Protocol):
    """Application-facing port; concrete model frameworks stay in infrastructure."""

    def predict(self, image: ImageFrame, confidence_threshold: float = 0.5) -> list[Detection]:
        ...
