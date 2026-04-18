from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional
import os
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    app_name: str = "Cortex-Dev"
    app_version: str = "1.0.0"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8000

    openai_api_key: str = ""
    gemini_api_key: str = ""

    @field_validator("debug", mode="before")
    @classmethod
    def _coerce_debug(cls, value):
        if isinstance(value, bool) or value is None:
            return bool(value)
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "y", "on", "debug"}:
                return True
            if normalized in {"0", "false", "no", "n", "off", "release", "prod", "production"}:
                return False
        return False

    @field_validator("port", mode="before")
    @classmethod
    def _coerce_port(cls, value):
        if value is None:
            return 8000
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value.strip())
            except ValueError:
                return 8000
        return 8000

    @property
    def allowed_origins(self) -> List[str]:
        """Get allowed origins with safe defaults"""
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8080",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
            "http://localhost:4000",
            "http://127.0.0.1:4000"
        ]
        
        # Add frontend URL from environment
        frontend_url = os.getenv("FRONTEND_URL")
        if frontend_url:
            origins.append(frontend_url)
        
        # Add production URLs if available
        if not self.debug:
            # In production, allow the deployed frontend
            render_frontend_url = os.getenv("RENDER_EXTERNAL_URL")
            if render_frontend_url:
                origins.append(render_frontend_url)
        
        return origins

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override port from environment if available (Render sets PORT)
        env_port = os.getenv("PORT")
        if env_port:
            try:
                self.port = int(env_port)
            except ValueError:
                logger.warning(f"Invalid PORT value: {env_port}, using default: {self.port}")


# Create settings instance with error handling
try:
    settings = Settings()
    logger.info(f"Settings loaded: {settings.app_name} v{settings.app_version}")
except Exception as e:
    logger.error(f"Failed to load settings: {e}")
    # Minimal fallback (avoid crashing on import)
    settings = Settings.model_construct(app_name="Cortex-Dev", app_version="1.0.0", debug=False, host="0.0.0.0", port=8000)
