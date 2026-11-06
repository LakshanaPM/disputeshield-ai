"""
DisputeShield AI — FastAPI Application Entry Point

Autonomous dispute defense agent for PayPal merchants.
Provides REST and WebSocket endpoints for dispute tracking, AI evidence
generation, risk analytics, and PayPal webhook ingestion.
"""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

# Ensure backend root is on sys.path for direct script execution
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config import settings
from database import engine, init_db
import models  # Ensure all ORM models are registered with Base.metadata
from api import (
    webhooks_router,
    disputes_router,
    analytics_router,
    ws_router,
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.app_debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("disputeshield")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Initializes database tables on startup and disposes of engine pool on shutdown.
    """
    logger.info("Starting DisputeShield AI API...")
    try:
        init_db()
        logger.info("Database tables verified / initialized successfully.")
    except Exception as exc:
        logger.warning(
            f"Database initialization deferred (database may still be starting): {exc}"
        )

    yield

    logger.info("Shutting down DisputeShield AI API...")
    try:
        engine.dispose()
        logger.info("Database connection pool disposed.")
    except Exception as exc:
        logger.error(f"Error during database disposal: {exc}")


# 1. Initialize FastAPI app with proper metadata
app = FastAPI(
    title="DisputeShield AI API",
    description="Autonomous dispute defense agent for PayPal merchants",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 2. Configure CORS middleware allowing origins from config.py & Render deployments
cors_origins = getattr(settings, "cors_origins", None) or [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https?://.*(onrender\.com|localhost:\d+)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Mount all existing routers under designated prefixes
app.include_router(webhooks_router, prefix="/api/webhooks")
app.include_router(disputes_router, prefix="/api/disputes")
app.include_router(analytics_router, prefix="/api/analytics")
app.include_router(ws_router, prefix="/ws")

# Clean webhook alias route: forward /webhooks/* requests to /api/webhooks/* for external PayPal compatibility
@app.api_route("/webhooks/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"], include_in_schema=False)
async def webhook_alias_redirect(full_path: str, request: Request):
    """Alias router to redirect legacy /webhooks/paypal requests to /api/webhooks/paypal seamlessly."""
    url = f"/api/webhooks/{full_path}"
    if request.url.query:
        url += f"?{request.url.query}"
    return RedirectResponse(url=url, status_code=307)


# 5. Implement /health GET endpoint
@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint for container probes and uptime monitoring."""
    return {"status": "ok", "app": "DisputeShield AI"}


@app.get("/", tags=["system"])
async def root():
    """Root endpoint returning service identity and documentation link."""
    return {
        "app": "DisputeShield AI",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
    )
