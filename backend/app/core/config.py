from datetime import timedelta
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ABPM Analyzer"
    secret_key: str = "super-secret-key"
    access_token_expire_minutes: int = 60 * 12
    algorithm: str = "HS256"
    database_url: str = "sqlite+aiosqlite:///./abpm.db"
    storage_dir: Path = Path("storage")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def access_token_expire_timedelta(self) -> timedelta:
        return timedelta(minutes=self.access_token_expire_minutes)


settings = Settings()
settings.storage_dir.mkdir(parents=True, exist_ok=True)
