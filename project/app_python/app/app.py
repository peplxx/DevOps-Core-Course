import logging
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.helpers import (
    get_current_timestamp,
    get_endpoints_list,
    get_request_info,
    get_runtime_info,
    get_service_info,
    get_system_info,
    get_uptime,
)
from app.logging_config import setup_logging  # Import our JSON logger
from app.settings import settings

# Configure JSON logging
logger = setup_logging(debug=settings.debug)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description
)

logger.info(
    "Application starting",
    extra={
        "app_name": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug,
        "host": settings.host,
        "port": settings.port
    }
)


# ===== Middleware for Request Logging =====

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing."""
    import time
    
    start_time = time.time()
    
    # Log request start
    logger.info(
        "Request started",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown")
        }
    )
    
    # Process request
    try:
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)
        
        # Log successful response
        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "client_ip": request.client.host if request.client else "unknown",
                "duration_ms": duration_ms
            }
        )
        
        return response
    except Exception as e:
        duration_ms = round((time.time() - start_time) * 1000, 2)
        
        # Log error
        logger.error(
            "Request failed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown",
                "duration_ms": duration_ms,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        raise


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

@app.get("/")
def root(request: Request) -> Dict[str, Any]:
    """Main endpoint returning comprehensive service and system information."""
    logger.debug(
        "Serving root endpoint",
        extra={
            "endpoint": "/",
            "client_ip": request.client.host if request.client else "unknown"
        }
    )
    
    return {
        "service": get_service_info(),
        "system": get_system_info(),
        "runtime": get_runtime_info(),
        "request": get_request_info(request),
        "endpoints": get_endpoints_list()
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    """Health check endpoint for monitoring and orchestration."""
    logger.debug("Health check requested", extra={"endpoint": "/health"})
    uptime = get_uptime()
    
    return {
        "status": "healthy",
        "timestamp": get_current_timestamp(),
        "uptime_seconds": uptime["seconds"]
    }
