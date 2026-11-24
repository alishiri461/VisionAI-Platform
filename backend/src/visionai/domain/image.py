"""Framework-neutral image value objects."""
from dataclasses import dataclass
from enum import Enum


class ColorOrder(str, Enum):
    BGR = "BGR"
    RGB = "RGB"
    GRAYSCALE = "GRAYSCALE"


@dataclass(frozen=True, slots=True)
class ImageFrame:
    """Decoded pixels with explicit metadata; the payload remains opaque to domain."""
    pixels: object
    width: int
    height: int
    channels: int
    color_order: ColorOrder

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Image dimensions must be positive.")
        if self.channels not in (1, 3, 4):
            raise ValueError("Image channel count must be 1, 3, or 4.")
