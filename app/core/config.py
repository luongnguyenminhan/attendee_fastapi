from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = (
        "postgresql+asyncpg://user:password@localhost:5432/attendee_fastapi_db"
    )
    SECRET_KEY: str = "your-super-secret-key-for-jwt"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # For regular access tokens
    LIFETIME_TOKEN_SECRET: str = "your-lifetime-token-secret"

    # Celery settings
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # Google Meet Integration settings (placeholders)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = ""


settings = Settings()
