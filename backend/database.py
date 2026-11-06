"""
DisputeShield AI — Database Engine & Session Management

SQLAlchemy async-compatible setup with PostgreSQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

from config import settings

# Engine kwargs configured conditionally by database dialect
engine_kwargs = {
    "pool_pre_ping": True,
    "echo": settings.app_debug,
}
if "sqlite" not in settings.database_url:
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
    })
else:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
LOCAL_DB_PATH = ROOT_DIR / "local_dev.db"

# Create engine with fallback for local dev environments
try:
    engine = create_engine(
        settings.database_url,
        **engine_kwargs,
    )
    # Test connection or dbapi load
    engine.connect()
except Exception:
    engine = create_engine(
        f"sqlite:///{LOCAL_DB_PATH.as_posix()}",
        connect_args={"check_same_thread": False},
    )

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    Automatically closes the session when the request is complete.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all database tables. Called on application startup."""
    Base.metadata.create_all(bind=engine)
