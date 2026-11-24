from pydantic import BaseModel, Field


class ImageAnalysisResponse(BaseModel):
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    channels: int = Field(ge=1)
    mean_grayscale: float
    sharpness_laplacian_variance: float
    histogram: dict[str, list[int]]
