import logging
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.settings import settings
from app.helpers import (
    get_service_info,
    get_system_info,
    get_runtime_info,
    get_request_info,
    get_endpoints_list,
    get_current_timestamp,
    get_uptime
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description
)

logger.info(f"Application starting... (version {settings.app_version})")


# ===== Error Handlers =====

@app.exception_handler(404)
async def not_found_handler(request: Request, exc) -> JSONResponse:
    """Handle 404 Not Found errors."""
    logger.warning(f"404 Not Found: {request.method} {request.url.path}")
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
    logger.error(f"500 Internal Server Error: {request.method} {request.url.path}")
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
    client_ip = request.client.host if request.client else "unknown"
    logger.debug(f"Request: {request.method} {request.url.path} from {client_ip}")
    
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
    logger.debug("Health check requested")
    uptime = get_uptime()
    
    return {
        "status": "healthy",
        "timestamp": get_current_timestamp(),
        "uptime_seconds": uptime["seconds"]
    }
