from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "WordDuel"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REDIS_URL: str = "redis://localhost:6379/0"

    # Cách cấu hình mới của Pydantic v2
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
