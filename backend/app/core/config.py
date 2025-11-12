from __future__ import annotations

from pathlib import Path
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Simple application settings used across the demo FastAPI app."""

    app_name: str = Field(default="ABPM Analyzer")
    storage_dir: Path = Field(default_factory=lambda: Path("storage"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
settings.storage_dir.mkdir(parents=True, exist_ok=True)
