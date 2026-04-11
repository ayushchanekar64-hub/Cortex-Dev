from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    app_name: str = "Cortex-Dev"
    app_version: str = "1.0.0"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", "8000"))

    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        os.getenv("FRONTEND_URL", "")
    ]

    openai_api_key: str = ""
    gemini_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
