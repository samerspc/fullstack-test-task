from functools import lru_cache
from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings sourced from environment variables.

    Single source of truth for DB/broker URLs, storage paths and tunables.
    Services and tasks read only from here, not from ``os.environ`` directly.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="test", alias="POSTGRES_DB")
    postgres_host: str = Field(default="backend-db", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="PGPORT")

    celery_broker_url: str = Field(default="redis://backend-redis:6379/0", alias="CELERY_BROKER_URL")

    storage_dir: Path = Field(
        default=Path(__file__).resolve().parents[2] / "storage" / "files",
        alias="STORAGE_DIR",
    )

    upload_chunk_size: int = Field(default=1024 * 1024, alias="UPLOAD_CHUNK_SIZE")
    suspicious_size_bytes: int = Field(default=10 * 1024 * 1024, alias="SUSPICIOUS_SIZE_BYTES")
    suspicious_extensions: tuple[str, ...] = (".exe", ".bat", ".cmd", ".sh", ".js")

    allowed_origins: tuple[str, ...] = (
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    )

    @computed_field
    @property
    def database_url_async(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field
    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
