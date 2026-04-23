import logging
import time
from typing import Any, Dict

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.helpers import (
    get_current_timestamp,
    get_endpoints_list,
    get_request_info,
    get_runtime_info,
    get_service_info,
    get_system_info,
    get_uptime,
)
from app.logging_config import setup_logging
from app.metrics import (
    devops_info_endpoint_calls,
    http_request_duration_seconds,
    http_requests_in_progress,
    http_requests_total,
)
from app.settings import settings
from app.visits import increment_visits, read_visits

logger = setup_logging(debug=settings.debug)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
)

logger.info(
    "Application starting",
    extra={
        "app_name": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug,
        "host": settings.host,
        "port": settings.port,
    },
)


# ===== Middleware for Request Logging & Metrics =====

METRICS_PATH = "/metrics"


@app.middleware("http")
async def log_and_track_requests(request: Request, call_next):
    """Log all HTTP requests and record Prometheus metrics."""
    if request.url.path == METRICS_PATH:
        return await call_next(request)

    start_time = time.time()
    endpoint = request.url.path
    method = request.method

    http_requests_in_progress.inc()

    logger.info(
        "Request started",
        extra={
            "method": method,
            "path": endpoint,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
        },
    )

    try:
        response = await call_next(request)
        duration = time.time() - start_time

        http_requests_total.labels(
            method=method, endpoint=endpoint, status=str(response.status_code)
        ).inc()
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

        logger.info(
            "Request completed",
            extra={
                "method": method,
                "path": endpoint,
                "status_code": response.status_code,
                "client_ip": request.client.host if request.client else "unknown",
                "duration_ms": round(duration * 1000, 2),
            },
        )
        return response
    except Exception as e:
        duration = time.time() - start_time

        http_requests_total.labels(method=method, endpoint=endpoint, status="500").inc()
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

        logger.error(
            "Request failed",
            extra={
                "method": method,
                "path": endpoint,
                "client_ip": request.client.host if request.client else "unknown",
                "duration_ms": round(duration * 1000, 2),
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )
        raise
    finally:
        http_requests_in_progress.dec()


# ===== Error Handlers =====

@app.exception_handler(404)
async def not_found_handler(request: Request, exc) -> JSONResponse:
    """Handle 404 Not Found errors."""
    logger.warning(
        "Endpoint not found",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
            "status_code": 404
        }
    )
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "Endpoint does not exist"
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc) -> JSONResponse:
    """Handle 500 Internal Server errors."""
    logger.error(
        "Internal server error",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
            "status_code": 500,
            "error": str(exc),
            "error_type": type(exc).__name__
        }
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )


# ===== API Endpoints =====


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
def root(request: Request) -> Dict[str, Any]:
    """Main endpoint returning comprehensive service and system information."""
    devops_info_endpoint_calls.labels(endpoint="/").inc()
    increment_visits()
    logger.debug(
        "Serving root endpoint",
        extra={
            "endpoint": "/",
            "client_ip": request.client.host if request.client else "unknown",
        },
    )

    return {
        "service": get_service_info(),
        "system": get_system_info(),
        "runtime": get_runtime_info(),
        "request": get_request_info(request),
        "endpoints": get_endpoints_list(),
    }


@app.get("/visits")
def visits() -> Dict[str, Any]:
    """Return the persisted visit count (root path hits)."""
    devops_info_endpoint_calls.labels(endpoint="/visits").inc()
    return {"visits": read_visits()}


@app.get("/health")
def health() -> Dict[str, Any]:
    """Health check endpoint for monitoring and orchestration."""
    devops_info_endpoint_calls.labels(endpoint="/health").inc()
    logger.debug("Health check requested", extra={"endpoint": "/health"})
    uptime = get_uptime()

    return {
        "status": "healthy",
        "timestamp": get_current_timestamp(),
        "uptime_seconds": uptime["seconds"],
    }
