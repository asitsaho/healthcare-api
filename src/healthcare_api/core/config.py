from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL, make_url


class Settings(BaseSettings):
    """Application configuration, loaded from environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Healthcare API"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://app:app@localhost:5433/app"

    @property
    def sqlalchemy_url(self) -> URL:
        return make_url(self.database_url)

    # Used only for the development/test actor identification scheme
    # described in the design doc (X-User-Id header). Replace with a real
    # authenticated identity (OAuth2/OIDC) in production.
    default_actor_header: str = "X-User-Id"

    default_page_limit: int = 20
    max_page_limit: int = 200

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
