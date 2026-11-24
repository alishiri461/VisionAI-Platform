"""Framework-neutral processing lifecycle contracts."""
from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass

from visionai.domain.image import ImageFrame


@dataclass(frozen=True, slots=True)
class ProcessingResult:
    success: bool
    data: object
    metadata: Mapping[str, object]
    error: str | None = None


class ProcessingEngine(ABC):
    """Lifecycle contract for pluggable image-processing engines."""

    @abstractmethod
    def initialize(self) -> None:
        """Load resources required by the engine."""

    @abstractmethod
    def process(self, image: ImageFrame) -> ProcessingResult:
        """Process one decoded image with explicit color semantics."""

    @abstractmethod
    def dispose(self) -> None:
        """Release engine resources."""
