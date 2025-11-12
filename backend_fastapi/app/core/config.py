from __future__ import annotations

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import secrets


class Settings(BaseSettings):
    PROJECT_NAME: str = "AdventureLog (FastAPI)"
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"
    DATABASE_URL: Optional[str] = None
    # PUBLIC_URL is used to build absolute media URLs (e.g. profile_pic) when returning user data.
    PUBLIC_URL: Optional[str] = None
    # Cookie settings for storing the access token. These are configurable via env.
    ACCESS_TOKEN_COOKIE_NAME: str = "access_token"
    ACCESS_TOKEN_COOKIE_SECURE: bool = False
    ACCESS_TOKEN_COOKIE_HTTPONLY: bool = True
    ACCESS_TOKEN_COOKIE_SAMESITE: str = "lax"  # 'lax' | 'strict' | 'none'
    ACCESS_TOKEN_COOKIE_PATH: str = "/"
    ACCESS_TOKEN_COOKIE_DOMAIN: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
