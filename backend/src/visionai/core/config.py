from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="VISIONAI_", env_file=".env", extra="ignore")
    max_upload_bytes: int = Field(default=10 * 1024 * 1024, ge=1024)
    max_image_width: int = Field(default=8000, gt=0)
    max_image_height: int = Field(default=8000, gt=0)
    max_image_pixels: int = Field(default=12_000_000, gt=0)
    allowed_origins_raw: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        validation_alias="VISIONAI_ALLOWED_ORIGINS",
    )

    @property
    def allowed_origins(self) -> list[str]:
        return [item.strip() for item in self.allowed_origins_raw.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
