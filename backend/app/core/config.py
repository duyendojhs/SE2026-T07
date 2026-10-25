"""Application configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    app_name: str = "GitHub Project Coach"
    app_env: str = "development"
    database_url: str = (
        "postgresql+psycopg://coach_user:coach_password@localhost:5432/github_coach_db"
    )
    redis_url: str = "redis://localhost:6379/0"

    github_app_id: int | None = None
    github_private_key: str | None = None
    github_private_key_path: str | None = None
    github_client_id: str | None = None
    github_client_secret: str | None = None
    github_webhook_secret: str | None = None
    github_api_url: str = "https://api.github.com"
    github_oauth_url: str = "https://github.com/login/oauth"
    github_oauth_redirect_uri: str = (
        "http://localhost:8000/api/v1/auth/github/callback"
    )
    github_app_slug: str | None = None

    session_secret: str = "dev-only-change-me-32-bytes-minimum"
    session_cookie_name: str = "gpc_session"
    oauth_state_cookie_name: str = "gpc_oauth_state"
    session_ttl_seconds: int = 86_400
    cookie_secure: bool = False

    audit_hmac_secret: str = "dev-only-change-me-32-bytes-minimum"
    backfill_days: int = 90
    github_reserve_requests: int = 100

    tenant_slug: str = "se2026-t07"
    tenant_name: str = "SE2026-T07 Entropy"
    frontend_url: str = "http://localhost:3000"
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""

    return Settings()


settings = get_settings()
