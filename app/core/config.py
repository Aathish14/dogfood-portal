"""Application configuration."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "DOGFOOD Portal"
    app_version: str = "0.1.0"
    debug: bool = False
    database_url: str = "sqlite:///./dogfood.db"
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    session_cookie_name: str = "session"
    session_cookie_secure: bool = False
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = "lax"
    fixtures_path: str = "./fixtures/fixtures.json"
    portal_base_url: str = "http://localhost:8080"
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


def get_database_path() -> Path:
    url = settings.database_url
    if url.startswith("sqlite:///"):
        path = url.replace("sqlite:///", "")
        return Path(path)
    return Path("./dogfood.db")
