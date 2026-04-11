from pydantic_settings import BaseSettings
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
        # Override port from environment if available
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
    # Create minimal fallback settings
    settings = Settings()
    settings.port = 8000
    settings.debug = False
