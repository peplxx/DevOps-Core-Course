import os
import platform
import socket
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import Request

from app.settings import settings

# Constants
FRAMEWORK_NAME = "FastAPI"
TIMEZONE = "UTC"
START_TIME = datetime.now(timezone.utc)


def get_current_timestamp() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def get_system_info() -> Dict[str, Any]:
    """Collect system information."""
    return {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "cpu_count": os.cpu_count(),
        "python_version": platform.python_version()
    }


def get_uptime() -> Dict[str, Any]:
    """Calculate application uptime."""
    delta = datetime.now(timezone.utc) - START_TIME
    seconds = int(delta.total_seconds())
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    return {
        "seconds": seconds,
        "human": f"{hours} hours, {minutes} minutes"
    }


def get_service_info() -> Dict[str, str]:
    """Get service metadata."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "framework": FRAMEWORK_NAME
    }


def get_runtime_info() -> Dict[str, Any]:
    """Get runtime information."""
    uptime = get_uptime()
    return {
        "uptime_seconds": uptime["seconds"],
        "uptime_human": uptime["human"],
        "current_time": get_current_timestamp(),
        "timezone": TIMEZONE
    }


def get_request_info(request: Request) -> Dict[str, str]:
    """Extract request information."""
    return {
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "method": request.method,
        "path": request.url.path
    }


def get_endpoints_list() -> list[Dict[str, str]]:
    """Get list of available endpoints."""
    return [
        {"path": "/", "method": "GET", "description": "Service information"},
        {"path": "/health", "method": "GET", "description": "Health check"},
        {"path": "/metrics", "method": "GET", "description": "Prometheus metrics"},
    ]
