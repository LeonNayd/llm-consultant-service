from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    APP_NAME: str = "auth-service"
    ENV: str = "local"

    JWT_SECRET: str = "change_me_super_secret"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    SQLITE_PATH: str = "./auth.db"

    @property
    def DATABASE_URL(self) -> str:
        """Формирует URL для подключения к SQLite."""
        return f"sqlite+aiosqlite:///{self.SQLITE_PATH}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()