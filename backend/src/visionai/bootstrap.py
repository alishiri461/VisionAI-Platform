"""Composition root for application dependency wiring."""
from visionai.application.use_cases.analyze_image import AnalyzeImageUseCase
from visionai.infrastructure.opencv.processor import OpenCvImageProcessor


def build_image_analysis_use_case() -> AnalyzeImageUseCase:
    """Construct the default image-analysis use case and its infrastructure adapter."""
    processor = OpenCvImageProcessor()
    return AnalyzeImageUseCase(decoder=processor, analyzer=processor)
