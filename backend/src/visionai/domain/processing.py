from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(slots=True)
class ProcessingResult:
    success: bool
    data: Any
    metadata: dict[str, Any]
    error: str | None = None


class ProcessingEngine(ABC):
    """Lifecycle contract for pluggable image-processing engines."""

    @abstractmethod
    def initialize(self) -> None:
        """Load resources required by the engine."""

    @abstractmethod
    def process(self, image: np.ndarray) -> ProcessingResult:
        """Process one decoded BGR image."""

    @abstractmethod
    def dispose(self) -> None:
        """Release engine resources."""
