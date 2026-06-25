from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "saas-template"
    APP_ENV: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite+aiosqlite:///./dev.db"

    JWT_SECRET_KEY: str = "CHANGE-ME-TO-A-RANDOM-SECRET-STRING"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    CORS_ORIGINS: str = "*"


settings = Settings()
