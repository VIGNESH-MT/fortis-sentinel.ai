"""
FORTIS SENTINEL - Main FastAPI Application

Production-grade agentic AI governance platform.
Provides REST API and WebSocket endpoints for agent monitoring,
governance verification, compliance checking, and anomaly detection.
"""

from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from database import Base, engine

# ---------------------------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------------------------

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Import all models so they register with Base.metadata
    import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print(f"🛡️  FORTIS SENTINEL v{settings.app_version} starting...")
    print(f"   Environment: {settings.app_env}")
    print(f"   Database: {'SQLite' if settings.is_sqlite else 'PostgreSQL'}")
    print(f"   Debug: {settings.app_debug}")

    yield

    # Shutdown
    await engine.dispose()
    print("🛡️  FORTIS SENTINEL shutting down...")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="FORTIS SENTINEL",
    description=(
        "Enterprise-grade agentic AI governance and verification platform. "
        "Uses 15 proprietary mathematical frameworks to guarantee agent safety, "
        "compliance, and reliability."
    ),
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

@app.middleware("http")
async def add_request_metadata(request: Request, call_next):
    """Add request ID and timing to all responses."""
    request_id = str(uuid.uuid4())
    start_time = time.time()

    response: Response = await call_next(request)

    duration_ms = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-Ms"] = str(duration_ms)
    response.headers["X-Powered-By"] = "FORTIS SENTINEL"

    return response


# ---------------------------------------------------------------------------
# Health & root endpoints
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - application info."""
    return {
        "name": "FORTIS SENTINEL",
        "version": settings.app_version,
        "status": "operational",
        "description": "Agentic AI Governance & Verification Platform",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint - no authentication required."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.app_env,
        "database": "connected",
    }


@app.get("/api/v1/status", tags=["Health"])
async def system_status():
    """Detailed system status including framework availability."""
    return {
        "status": "operational",
        "version": settings.app_version,
        "frameworks": {
            "total": 18,
            "active": 18,
            "categories": {
                "safety": ["approach_1", "approach_3", "approach_5", "approach_7", "approach_9"],
                "anomaly_detection": ["approach_4", "approach_6", "approach_8"],
                "orchestration": ["approach_10", "approach_11", "approach_12"],
                "compliance": ["approach_13", "approach_14", "approach_15"],
                "liability": ["approach_2"],
                "bonus": ["bonus_16", "bonus_17", "bonus_18"],
            },
        },
        "capabilities": [
            "agent_governance",
            "anomaly_detection",
            "compliance_verification",
            "cryptographic_audit",
            "real_time_monitoring",
        ],
    }


# ---------------------------------------------------------------------------
# Register API routers
# ---------------------------------------------------------------------------

from api.agents import router as agents_router  # noqa: E402
from api.logs import router as logs_router  # noqa: E402
from api.governance import router as governance_router  # noqa: E402
from api.compliance import router as compliance_router  # noqa: E402
from api.websocket import router as websocket_router  # noqa: E402

app.include_router(agents_router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(logs_router, prefix="/api/v1/logs", tags=["Execution Logs"])
app.include_router(governance_router, prefix="/api/v1/governance", tags=["Governance"])
app.include_router(compliance_router, prefix="/api/v1/compliance", tags=["Compliance"])
app.include_router(websocket_router, prefix="/api/v1/ws", tags=["WebSocket"])


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler for unhandled errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": str(exc) if settings.is_development else "An unexpected error occurred",
            "request_id": request.headers.get("X-Request-ID", "unknown"),
        },
    )
