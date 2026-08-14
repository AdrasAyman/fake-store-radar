from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://radar:dev@localhost:5432/radar"
    redis_url: str = "redis://localhost:6379/0"
    certstream_url: str = "wss://certstream.calidog.io/"


settings = Settings()
