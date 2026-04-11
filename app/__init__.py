"""
Cortex-Dev - AI SaaS Backend Application

This package contains the main FastAPI application for the Cortex-Dev AI SaaS platform.
"""

__version__ = "1.0.0"
__author__ = "Cortex-Dev Team"
__description__ = "AI-powered development agent backend"

# Import main application
from app.main import app
from app.config.settings import settings

__all__ = ["app", "settings", "__version__"]