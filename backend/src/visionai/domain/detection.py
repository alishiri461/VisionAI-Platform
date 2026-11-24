from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass(frozen=True, slots=True)
class Detection:
    label: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float


class ObjectDetector(Protocol):
    """Adapter contract; concrete model runtimes are added in the detection phase."""

    def predict(
        self,
        image: np.ndarray,
        confidence_threshold: float = 0.5,
    ) -> list[Detection]:
        ...
