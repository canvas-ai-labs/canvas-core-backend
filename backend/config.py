from functools import lru_cache
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env when present
load_dotenv()


class Settings(BaseSettings):
    """Typed application settings loaded from environment variables.

    Validation is deferred to service initialization time so the app can boot even
    if optional features (e.g., Canvas/LLM) are not configured.
    """

    canvas_api_url: Optional[str] = None
    canvas_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    database_url: Optional[str] = None

    # CORS
    allowed_origins: List[str] = Field(default_factory=lambda: ["*"])

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",  # allow extra env vars in .env without failing
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _split_origins(cls, v):
        if v is None:
            return ["*"]
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
