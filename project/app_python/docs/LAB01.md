# Lab 01 - DevOps Info Service

**Student Name**: Melnikov Sergei (s.melnikov@innopolis.university) 
**Date**: January 28, 2026  
**Lab**: Lab 01 - Web Application Development

## 1. Framework Selection

### Chosen Framework: FastAPI

**Decision Rationale:**

I selected FastAPI for this project based on the following key factors:

1. **Modern Python Features** - FastAPI leverages Python 3.6+ type hints, providing excellent IDE support and automatic data validation
2. **Automatic API Documentation** - Built-in Swagger UI and ReDoc for interactive API documentation
3. **High Performance** - Built on Starlette and Pydantic, FastAPI rivals Node.js and Go in speed
4. **Async Support** - Native async/await support for handling concurrent requests efficiently
5. **Easy to Learn** - Clear, intuitive API design with excellent documentation

### Framework Comparison

| Feature | FastAPI | Flask | Django |
|---------|---------|-------|--------|
| **Performance** | Very High (async) | Medium | Medium |
| **Learning Curve** | Easy | Very Easy | Moderate-Hard |
| **API Documentation** | Automatic (OpenAPI) | Manual | Manual/DRF |
| **Async Support** | Native | Limited (3.x) | Limited |
| **Type Hints** | Required/Validated | Optional | Optional |
| **Built-in Features** | Minimal + Powerful | Minimal | Extensive (ORM, Admin) |
| **Best For** | APIs, Microservices | Small-Medium Apps | Full Web Apps |
| **Community Size** | Growing Fast | Very Large | Very Large |

**Conclusion**: FastAPI provides the best balance of performance, modern features, and ease of use for a microservice that will evolve into a comprehensive DevOps monitoring tool.

## 2. Best Practices Applied

### 2.1 Clean Code Organization

**Practice**: Separated concerns into multiple modules for better maintainability.

```python
# Project structure
app/
├── __main__.py      # Entry point
├── app.py           # FastAPI routes and error handlers
├── helpers.py       # Business logic and utilities
└── settings.py      # Configuration management
```

**Why it matters**: Separation of concerns makes code easier to test, maintain, and extend. Each module has a single responsibility.

### 2.2 Type Hints

**Practice**: Used comprehensive type hints throughout the codebase.

```python
def get_system_info() -> Dict[str, Any]:
    """Collect system information."""
    return {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        # ...
    }

def get_request_info(request: Request) -> Dict[str, str]:
    """Extract request information."""
    return {
        "client_ip": request.client.host if request.client else "unknown",
        # ...
    }
```

**Why it matters**: Type hints provide better IDE support, catch errors early, and serve as inline documentation. FastAPI uses them for automatic validation.

### 2.3 Configuration Management with Pydantic Settings

**Practice**: Used pydantic-settings for type-safe environment variable management.

```python
# app/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )

settings = Settings()
```

**Why it matters**: Provides validation, type safety, and clear documentation of all configuration options. Supports multiple configuration sources (.env files, environment variables).

### 2.4 Error Handling

**Practice**: Implemented custom error handlers for common HTTP errors.

```python
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
```

**Why it matters**: Consistent error responses improve API usability. Logging errors helps with debugging and monitoring in production.

### 2.5 Structured Logging

**Practice**: Configured structured logging with appropriate levels.

```python
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Usage
logger.info(f"Application starting... (version {settings.app_version})")
logger.debug(f"Request: {request.method} {request.url.path} from {client_ip}")
```

**Why it matters**: Proper logging is crucial for debugging, monitoring, and understanding application behavior in production. Different log levels allow filtering based on environment.

### 2.6 Constants and DRY Principle

**Practice**: Defined constants for values used multiple times.

```python
# Constants
FRAMEWORK_NAME = "FastAPI"
TIMEZONE = "UTC"
START_TIME = datetime.now(timezone.utc)
```

**Why it matters**: Reduces code duplication (DRY - Don't Repeat Yourself) and makes updates easier. Changing a constant in one place updates all usages.

### 2.7 Comprehensive Documentation

**Practice**: Added docstrings to all functions and modules.

```python
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
```

**Why it matters**: Good documentation helps other developers (and future you) understand the code quickly. FastAPI uses docstrings to generate API documentation.

### 2.8 Dependency Management

**Practice**: Created both `requirements.txt` and `pyproject.toml` with pinned versions.

```txt
# requirements.txt
fastapi==0.128.0
uvicorn[standard]==0.40.0
pydantic==2.12.5
pydantic-settings==2.12.0
```

**Why it matters**: Pinned versions ensure reproducible builds across different environments. Prevents "works on my machine" issues.

### 2.9 Environment Configuration

**Practice**: Created `.env.example` template and proper `.gitignore`.

```bash
# .env.example
HOST=0.0.0.0
PORT=5000
DEBUG=false

# .gitignore includes:
.env
.env.*
!.env.example
```

**Why it matters**: Prevents accidentally committing secrets while providing a template for new developers. Security best practice.

### 2.10 Build Automation with Makefile

**Practice**: Created a Makefile for common development tasks.

```makefile
# Key commands
make help       # Show all available commands
make env        # Create .env from template
make install    # Install dependencies
make run        # Run in production mode
make dev        # Run in development mode
make format     # Format and fix code with ruff
make clean      # Clean cache files
make info       # Show environment info
```

**Why it matters**: Simplifies common tasks, provides consistent commands across the team, and reduces cognitive load. New developers can quickly understand available operations with `make help`. The `make format` command ensures code style consistency automatically.

## 3. API Documentation

### 3.1 Main Endpoint: `GET /`

**Description**: Returns comprehensive service and system information.

**Request Example:**
```bash
curl http://localhost:5000/
```

**Response Example:**
```json
{
  "service": {
    "name": "devops-info-service",
    "version": "1.0.0",
    "description": "DevOps course info service",
    "framework": "FastAPI"
  },
  "system": {
    "hostname": "MacBook-Pro.local",
    "platform": "Darwin",
    "platform_version": "Darwin Kernel Version 25.2.0",
    "architecture": "arm64",
    "cpu_count": 8,
    "python_version": "3.14.1"
  },
  "runtime": {
    "uptime_seconds": 45,
    "uptime_human": "0 hours, 0 minutes",
    "current_time": "2026-01-28T12:00:00.123456+00:00",
    "timezone": "UTC"
  },
  "request": {
    "client_ip": "127.0.0.1",
    "user_agent": "curl/8.7.1",
    "method": "GET",
    "path": "/"
  },
  "endpoints": [
    {"path": "/", "method": "GET", "description": "Service information"},
    {"path": "/health", "method": "GET", "description": "Health check"}
  ]
}
```

### 3.2 Health Check: `GET /health`

**Description**: Simple health check endpoint for monitoring and orchestration.

**Request Example:**
```bash
curl http://localhost:5000/health
```

**Response Example:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-28T12:00:00.123456+00:00",
  "uptime_seconds": 45
}
```

### 3.3 Testing Commands

**Using Makefile:**
```bash
# Start the application
make run        # Production mode
make dev        # Development mode

# Check configuration
make info       # Show environment details
```

**Using curl:**
```bash
# Basic test
curl http://localhost:5000/

# Pretty-printed output
curl http://localhost:5000/ | python -m json.tool

# Test with custom port
PORT=8080 uv run -m app &
curl http://localhost:8080/

# Test health endpoint
curl http://localhost:5000/health

# Test error handling (404)
curl http://localhost:5000/nonexistent

# Load test with multiple requests
for i in {1..10}; do curl -s http://localhost:5000/health; done
```

## 4. Testing Evidence

### Screenshots

Screenshots demonstrating the working application are located in `docs/screenshots/`:

1. **01-main-endpoint.png** - Main endpoint showing complete JSON response
2. **02-health-check.png** - Health check endpoint response
3. **03-formatted-output.png** - Pretty-printed JSON output
4. **04-uvicorn-startup.png** - Application startup logs
5. **05-debug-mode.png** - Debug mode with detailed logging

### Terminal Output

**Application Startup:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
```

**Request Logs:**
```
2026-01-28 12:00:00,123 - app.app - INFO - Application starting... (version 1.0.0)
2026-01-28 12:00:15,456 - app.app - DEBUG - Request: GET / from 127.0.0.1
INFO:     127.0.0.1:54321 - "GET / HTTP/1.1" 200 OK
2026-01-28 12:00:20,789 - app.app - DEBUG - Health check requested
INFO:     127.0.0.1:54322 - "GET /health HTTP/1.1" 200 OK
```

## 5. Challenges & Solutions

### Challenge 1: Module Import Structure

**Problem**: Initially struggled with circular imports and proper module organization.

**Solution**: Restructured the application into separate modules (`app.py`, `helpers.py`, `settings.py`) with clear dependencies. Settings are imported by helpers, helpers are imported by app, avoiding circular dependencies.

### Challenge 2: Pydantic Settings Configuration

**Problem**: Needed to understand how pydantic-settings handles environment variables and .env files with proper type validation.

**Solution**: Studied the pydantic-settings documentation and configured `SettingsConfigDict` with appropriate options (`case_sensitive=False`, `env_file=".env"`). This provides flexibility in environment variable naming.

### Challenge 3: Uptime Calculation Persistence

**Problem**: Needed application uptime to persist across requests but reset on restart.

**Solution**: Stored `START_TIME` as a module-level constant in `helpers.py`, which is initialized once when the module is imported. This persists for the application lifetime but resets on restart.

### Challenge 4: Request Information Extraction

**Problem**: FastAPI's Request object structure differs from Flask, needed to understand how to extract client IP and headers correctly.

**Solution**: Used `request.client.host` for IP (with fallback to "unknown") and `request.headers.get()` for headers. Added defensive checks for cases where `request.client` might be None (e.g., during testing).

### Challenge 5: Logging Configuration

**Problem**: Wanted different log levels for development vs production without code changes.

**Solution**: Used the `DEBUG` environment variable to dynamically set the logging level:
```python
level=logging.DEBUG if settings.debug else logging.INFO
```

### Challenge 6: Developer Experience

**Problem**: Needed to simplify common development tasks to reduce friction and make the project more accessible.

**Solution**: Created a Makefile with intuitive commands that handle environment setup, dependency installation, and running the application. The `make help` command provides self-documenting interface showing all available operations. This makes onboarding new developers faster and ensures consistency across the team.

## 6. GitHub Community

### Actions Completed

- ✅ Starred the course repository
- ✅ Starred [simple-container-com/api](https://github.com/simple-container-com/api)
- ✅ Followed professor [@Cre-eD](https://github.com/Cre-eD)
- ✅ Followed TA [@marat-biriushev](https://github.com/marat-biriushev)
- ✅ Followed TA [@pierrepicaud](https://github.com/pierrepicaud)
- ✅ Followed 3+ classmates from the course

## 7. Conclusion

This lab provided a solid foundation in modern Python web development and DevOps practices. By implementing FastAPI with proper configuration management, error handling, and logging, I've created a maintainable service that will evolve throughout the course. The emphasis on best practices and documentation ensures the codebase is production-ready and extensible for future labs.

**Key Takeaways:**
- FastAPI's automatic validation and documentation significantly improve development speed
- Proper separation of concerns makes code more maintainable and testable
- Configuration management is critical for deploying across different environments
- Comprehensive logging and error handling are essential for production services
- Documentation and code organization matter as much as functionality
- Build automation (Makefile) improves developer experience and team consistency

---

**Lab Status**: ✅ Complete  
**Next Steps**: Lab 02 - Containerization with Docker
