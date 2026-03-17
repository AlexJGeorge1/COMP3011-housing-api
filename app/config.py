from pydantic_settings import BaseSettings
from functools import lru_cache


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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — reads .env once at startup."""
    return Settings()
