from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os
import logging

logger = logging.getLogger(__name__)

def _default_sqlite_url() -> str:
    """
    Render (and some other PaaS) deploys often have a read-only app dir.
    When DATABASE_URL isn't provided, default to a writable location.
    """
    is_render = bool(
        os.getenv("RENDER")
        or os.getenv("RENDER_SERVICE_ID")
        or os.getenv("RENDER_EXTERNAL_URL")
    )
    if is_render:
        return "sqlite:////tmp/auto_dev.db"
    return "sqlite:///./auto_dev.db"


# Use environment variable for database URL or fallback to SQLite
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL") or _default_sqlite_url()

# Configure engine based on database type
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database with error handling"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Don't raise - allow app to continue without DB

def get_db():
    """Get database session with error handling"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
    finally:
        db.close()
