from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Cortex-Dev",
    description="AI-powered development agent backend",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize database and other startup tasks"""
    try:
        # Import here to avoid circular imports
        from app.database import init_db
        from app.config.settings import settings
        
        # Initialize database
        init_db()
        logger.info("Database initialized successfully")
        
        # Log startup info
        logger.info(f"Starting {settings.app_name} v{settings.app_version}")
        logger.info(f"Allowed origins: {settings.allowed_origins}")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        # Continue startup even if DB fails

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Incoming Request: {request.method} {request.url.path}")
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(f"Completed Request: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.2f}ms")
    return response

# Configure CORS with safe defaults
@app.on_event("startup")
async def configure_cors():
    """Configure CORS after settings are loaded"""
    try:
        from app.config.settings import settings
        
        # Filter out empty origins
        allowed_origins = [origin for origin in settings.allowed_origins if origin]
        
        # Add production frontend URL if available
        frontend_url = os.getenv("FRONTEND_URL")
        if frontend_url and frontend_url not in allowed_origins:
            allowed_origins.append(frontend_url)
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins or ["*"],  # Fallback to allow all
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.info(f"CORS configured with origins: {allowed_origins}")
        
    except Exception as e:
        logger.error(f"CORS configuration failed: {e}")
        # Add basic CORS as fallback
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

# Include routers with error handling
@app.on_event("startup")
async def include_routers():
    """Include all API routers"""
    try:
        from app.routes import (
            generate, planner, generator, debug, tester, 
            pipeline, auth, projects, github, templates
        )
        
        routers = [
            generate.router,
            planner.router,
            generator.router,
            debug.router,
            tester.router,
            pipeline.router,
            auth.router,
            projects.router,
            github.router,
            templates.router
        ]
        
        for router in routers:
            app.include_router(router, prefix="/api")
        
        logger.info("All routers included successfully")
        
    except Exception as e:
        logger.error(f"Failed to include routers: {e}")
        # Continue with basic app even if routers fail

@app.get("/")
async def root():
    return {"status": "active"}
