from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql://postgres:postgres@localhost:5432/mlops_tracker"
    redis_url: str = "redis://localhost:6379"
    secret_key: str = "dev-secret-key"
    api_key: str = "dev-api-key"
    flask_env: str = "development"

    @property
    def is_testing(self) -> bool:
        return self.flask_env == "testing"


settings = Settings()
