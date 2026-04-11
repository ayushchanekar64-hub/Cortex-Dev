from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

from app.config.settings import settings
from app.routes import generate, planner, generator, debug, tester, pipeline, auth, projects, github, templates
from app.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO, # Force INFO level for debugging
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Database
init_db()

# Create FastAPI application
app = FastAPI(
    title="Cortex-Dev",
    description="AI-powered development agent backend",
    version="1.0.0"
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Incoming Request: {request.method} {request.url.path}")
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(f"Completed Request: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.2f}ms")
    return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generate.router, prefix="/api")
app.include_router(planner.router, prefix="/api")
app.include_router(generator.router, prefix="/api")
app.include_router(debug.router, prefix="/api")
app.include_router(tester.router, prefix="/api")
app.include_router(pipeline.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(github.router, prefix="/api")
app.include_router(templates.router, prefix="/api")

@app.get("/")
async def root():
    return {"status": "active"}
