"""
SUPER RR — CLUTCH IQ
FastAPI Backend Application Entrypoint
"""

import time
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.api.config import settings
from backend.api.dependencies import get_data_service
from backend.api.routes import (
    health,
    leaderboards,
    players,
    archetypes,
    analytics
)

logger = logging.getLogger("superrr.clutch_iq.api")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Initializes data caches and pre-indexes lookups on startup.
    """
    logger.info("Initializing CLUTCH IQ Data Service caches...")
    service = get_data_service()
    service.initialize()
    logger.info("Data caches loaded successfully. Backend ready.")
    yield
    logger.info("CLUTCH IQ Backend shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Production REST API for SUPER RR — CLUTCH IQ: Beyond Statistics. "
        "Exposes cricket analytics, pressure segmentation, Bayesian-shrunk Clutch IQ "
        "rankings, and unsupervised K-Means player archetypes."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ---------------------------------------------------------
# CORS Middleware
# ---------------------------------------------------------
has_wildcard = "*" in settings.CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if has_wildcard else settings.CORS_ORIGINS,
    allow_credentials=not has_wildcard,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Response Timing & Telemetry Middleware
# ---------------------------------------------------------
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time_ms = (time.perf_counter() - start_time) * 1000.0
    response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"
    return response


# ---------------------------------------------------------
# Global Exception Handlers
# ---------------------------------------------------------
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    msg_parts = []
    for err in errors:
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        msg_parts.append(f"{loc}: {err.get('msg', 'validation error')}")
    formatted_msg = "; ".join(msg_parts) if msg_parts else "Invalid request parameters"
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": f"Request validation error: {formatted_msg}",
            "status_code": 422,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled server error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred.",
            "status_code": 500,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


# ---------------------------------------------------------
# Root & Top-Level Probes
# ---------------------------------------------------------
@app.get("/", summary="Root Welcome & Metadata", tags=["Root"])
def root_endpoint() -> Dict[str, Any]:
    return {
        "project": settings.PROJECT_NAME,
        "slogan": settings.PROJECT_SLOGAN,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_v1_base": settings.API_V1_PREFIX,
        "health_endpoint": f"{settings.API_V1_PREFIX}/health"
    }


# Duplicate root-level health probe for container/orchestrator health checks
@app.get("/health", summary="Top-Level Health Probe", tags=["System & Metadata"])
def root_health_check() -> Dict[str, Any]:
    service = get_data_service()
    return service.get_health_status()


# ---------------------------------------------------------
# Mount API v1 Routers
# ---------------------------------------------------------
app.include_router(health.router, prefix=settings.API_V1_PREFIX)
app.include_router(leaderboards.router, prefix=settings.API_V1_PREFIX)
app.include_router(players.router, prefix=settings.API_V1_PREFIX)
app.include_router(archetypes.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=port, reload=False)
