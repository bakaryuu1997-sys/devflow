from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DevFlow Guard"
    database_url: str = "sqlite:///./devflow.db"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 525600
    environment: str = "development"
    auto_create_tables: bool = True
    allow_demo_reset: bool = True
    cors_origins: str = "http://localhost:8000,http://localhost:5173"
    sentry_dsn: str = ""
    allow_public_register: bool = True
    auth_mode: str = "local"
    local_write_auth_required: bool = False
    require_secure_production: bool = True

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
