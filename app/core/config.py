from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote, urlsplit, urlunsplit

class Settings(BaseSettings):
    PROJECT_NAME: str = "WordDuel"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REDIS_URL: str | None = None
    REDIS_PASSWORD: str | None = None
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    CORS_ORIGIN_REGEX: str = r"^https?://(localhost|127\.0\.0\.1|10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})(:\d+)?$"

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def redis_connection_url(self) -> str:
        """Use REDIS_PASSWORD for the local Compose Redis unless URL has credentials."""
        url = self.REDIS_URL or "redis://localhost:6379/0"
        if not self.REDIS_PASSWORD:
            return url

        parsed = urlsplit(url)
        if parsed.password is not None:
            return url

        host = parsed.netloc.rsplit("@", 1)[-1]
        username = f"{quote(parsed.username, safe='')}" if parsed.username else ""
        credentials = f"{username}:{quote(self.REDIS_PASSWORD, safe='')}@"
        return urlunsplit(parsed._replace(netloc=f"{credentials}{host}"))

    # Cách cấu hình mới của Pydantic v2
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
