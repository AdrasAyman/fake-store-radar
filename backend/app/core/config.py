import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://radar:dev@localhost:5432/radar"
    redis_url: str = "redis://localhost:6379/0"
    certstream_url: str = "wss://certstream.calidog.io/"

    # macOS ships Python without access to the system trust store, so TLS
    # verification fails unless we point it at certifi's CA bundle.
    ssl_cert_file: str | None = None


settings = Settings()

if settings.ssl_cert_file:
    os.environ.setdefault("SSL_CERT_FILE", settings.ssl_cert_file)
    os.environ.setdefault("REQUESTS_CA_BUNDLE", settings.ssl_cert_file)