from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    cors_origins: str
    secret_key: str
    cookie_secure: bool = False
    session_max_age_seconds: int = 60 * 60 * 24 * 7

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
