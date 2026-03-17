import logging
from pydantic_settings import BaseSettings
from pydantic import model_validator
from functools import lru_cache

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # ── Database ───────────────────────────────────────────────────────────────
    database_url: str

    # ── Authentication ─────────────────────────────────────────────────────────
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # ── Demo credentials (development only) ───────────────────────────────────
    demo_username: str = "admin"
    demo_password: str = "secret"

    # ── AI / LLM ──────────────────────────────────────────────────────────────
    # Optional — the /insights endpoint degrades gracefully if absent
    groq_api_key: str | None = None

    @model_validator(mode="after")
    def _warn_default_credentials(self):
        if self.demo_password == "secret":
            logger.warning(
                "DEMO_PASSWORD is still set to the default value 'secret'. "
                "Change it before deploying to production."
            )
        return self

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — reads .env once at startup."""
    return Settings()
