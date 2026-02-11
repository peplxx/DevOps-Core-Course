# DevOps Info Service

[![Python CI (app_python)](https://github.com/peplxx/DevOps-Core-Course/actions/workflows/python-ci.yml/badge.svg?branch=master)](https://github.com/peplxx/DevOps-Core-Course/actions/workflows/python-ci.yml)

A FastAPI-based web service that provides comprehensive system information and health status. This service is designed to evolve throughout the DevOps Core Course, serving as a foundation for containerization, CI/CD, monitoring, and deployment practices.

## Overview

The DevOps Info Service exposes RESTful endpoints that return detailed information about:
- Service metadata (name, version, framework)
- System information (hostname, platform, architecture, CPU, Python version)
- Runtime metrics (uptime, current time)
- Request details (client IP, user agent, method, path)
- Health status for monitoring and orchestration

## Prerequisites

- **Python**: 3.11 or higher (CI uses 3.11+)
- **Package Manager**: `uv` (recommended) or `pip`
- **Operating System**: Linux, macOS, or Windows

## Installation

### Quick Start with Makefile (Recommended)

```bash
# Complete setup in two commands
make env        # Create .env file from template
make install    # Install all dependencies

# Or use the combined setup command
make env install
```

### Manual Installation

#### Using uv (Recommended)

```bash
# Install dependencies
uv sync
```

#### Using pip and venv

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install .
```

## Running the Application

### Using Makefile (Recommended)

```bash
# Run in production mode
make run

# Run in development mode (with auto-reload)
make dev

# Check environment configuration
make info

# View all available commands
make help
```

### Manual Execution

#### Default Configuration

```bash
# Using uv
uv run -m app

# Using Python directly
python -m app
```

The service will start on `http://0.0.0.0:5000` by default.

## Docker

You can run the service as a container (Lab 2).

- **Build the image locally**: run `docker build` from the `app_python/` directory and tag it as `<name>:<tag>`.
- **Run a container**: run `docker run` with port publishing (`-p <host_port>:5000`) and an optional container name. The app listens on port `5000` inside the container by default.
- **Pull from Docker Hub**: `docker pull <dockerhub_user>/<repo>:<tag>`, then run it the same way as the local image.

#### Custom Configuration

You can configure the service using environment variables:

```bash
# Custom port
PORT=8080 uv run -m app

# Custom host and port
HOST=127.0.0.1 PORT=3000 uv run -m app

# Development mode with auto-reload
DEBUG=true uv run -m app
```

#### Using .env File

Create a `.env` file from the example:

```bash
# Using Makefile
make env

# Or manually
cp .env.example .env
# Edit .env with your preferred settings
uv run -m app
```

## API Endpoints

### `GET /` - Service Information

Returns comprehensive service and system information.

**Example Request:**
```bash
curl http://localhost:5000/
```

**Example Response:**
```json
{
  "service": {
    "name": "devops-info-service",
    "version": "1.0.0",
    "description": "DevOps course info service",
    "framework": "FastAPI"
  },
  "system": {
    "hostname": "my-laptop",
    "platform": "Darwin",
    "platform_version": "Darwin Kernel Version 25.2.0",
    "architecture": "arm64",
    "cpu_count": 8,
    "python_version": "3.14.1"
  },
  "runtime": {
    "uptime_seconds": 120,
    "uptime_human": "0 hours, 2 minutes",
    "current_time": "2026-01-28T12:00:00.000000+00:00",
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

### `GET /health` - Health Check

Simple health check endpoint for monitoring and orchestration tools (e.g., Kubernetes probes).

**Example Request:**
```bash
curl http://localhost:5000/health
```

**Example Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-28T12:00:00.000000+00:00",
  "uptime_seconds": 120
}
```

## Configuration

The application can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host address |
| `PORT` | `5000` | Server port number |
| `DEBUG` | `false` | Enable debug mode with auto-reload |
| `APP_NAME` | `devops-info-service` | Application name |
| `APP_VERSION` | `1.0.0` | Application version |
| `APP_DESCRIPTION` | `DevOps course info service` | Application description |

## Project Structure

```
app_python/
├── app/
│   ├── __init__.py
│   ├── __main__.py          # Application entry point
│   ├── app.py               # FastAPI application and routes
│   ├── helpers.py           # Helper functions
│   └── settings.py          # Configuration management
├── tests/                   # Unit tests (Lab 3)
│   └── __init__.py
├── docs/                    # Documentation
│   ├── LAB01.md            # Lab submission
│   └── screenshots/        # Testing evidence
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── Makefile                # Build automation
├── pyproject.toml          # Project metadata and dependencies
├── README.md               # This file
└── uv.lock                 # Locked dependencies (uv)
```

## Development

### Running in Development Mode

```bash
# Using Makefile (recommended)
make dev

# Or manually
DEBUG=true uv run -m app
```

This enables:
- Auto-reload on code changes
- Debug-level logging
- Detailed error messages

### Testing the API

```bash
# Test main endpoint
curl http://localhost:5000/

# Test health check
curl http://localhost:5000/health

# Pretty-print JSON output
curl http://localhost:5000/ | python -m json.tool

# Using httpie (if installed)
http http://localhost:5000/
```

### Makefile Commands

```bash
make help       # Show all available commands
make env        # Create .env from template
make install    # Install dependencies
make run        # Run in production mode
make dev        # Run in development mode
make format     # Format and fix code with ruff
make lint       # Lint code with ruff
make test       # Run unit tests (pytest)
make clean      # Clean cache files
make info       # Show environment info
```

## Testing (Lab 3)

### Run tests with uv (recommended)

```bash
cd project/app_python
uv sync --dev
uv run pytest
```

### Run tests with Makefile

```bash
cd project/app_python
make install
make test
```

## Technologies Used

- **FastAPI** - Modern, fast web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation and settings management
- **Python 3.11+** - Supported by CI

## Future Enhancements

This service will evolve throughout the course:
- **Lab 2**: Containerization with Docker
- **Lab 3**: Unit tests and CI/CD pipeline
- **Lab 8**: Prometheus metrics endpoint
- **Lab 9**: Kubernetes deployment
- **Lab 12**: Persistence with file storage

## License

This project is part of the DevOps Core Course.

## Author

Melnikov Sergei (s.melnikov@innopolis.university)

Created for the DevOps Core Course - Lab 1
