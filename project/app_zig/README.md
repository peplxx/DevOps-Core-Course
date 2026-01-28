# DevOps Info Service (Zig Implementation)

A high-performance implementation of the DevOps Info Service using Zig, providing the same API as the Python version with significantly smaller binary size and faster startup time.

## Overview

This is the bonus task implementation for Lab 01, showcasing Zig's capabilities for building efficient system services. The service provides comprehensive system information and health status through RESTful endpoints.

## Prerequisites

- **Zig**: 0.15.2
- **Operating System**: Linux, macOS, or Windows

## Installation

### Install Zig

```bash
# macOS (Homebrew)
brew install zig

# Or download from https://ziglang.org/download/
```

For this repo we target **Zig 0.15.2**.

## Building

### Development Build

```bash
zig build
```

### Optimized Release Build

```bash
# Release with size optimization
zig build -Doptimize=ReleaseSmall

# Release with speed optimization  
zig build -Doptimize=ReleaseFast

# Release with safety checks
zig build -Doptimize=ReleaseSafe
```

The compiled binary will be in `zig-out/bin/devops-info-service`.

## Running

### Default Configuration

```bash
# Run directly with zig
zig build run

# Or run the compiled binary
./zig-out/bin/devops-info-service
```

The service will start on `http://0.0.0.0:8080` by default.

### Custom Configuration

```bash
# Custom port
PORT=3000 ./zig-out/bin/devops-info-service

# Custom host and port
HOST=127.0.0.1 PORT=3000 ./zig-out/bin/devops-info-service
```

## API Endpoints

### `GET /` - Service Information

Returns comprehensive service and system information.

**Example:**
```bash
curl http://localhost:8080/
```

**Response:**
```json
{
  "service": {
    "name": "devops-info-service",
    "version": "1.0.0",
    "description": "DevOps course info service",
    "framework": "Zig std.http"
  },
  "system": {
    "hostname": "my-laptop",
    "platform": "macos",
    "platform_version": "macOS",
    "architecture": "aarch64",
    "cpu_count": 8,
    "zig_version": "0.15.2"
  },
  "runtime": {
    "uptime_seconds": 45,
    "uptime_human": "0 hours, 0 minutes",
    "current_time": "2026-01-28T12:00:00Z",
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

Simple health check endpoint for monitoring.

**Example:**
```bash
curl http://localhost:8080/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-28T12:00:00Z",
  "uptime_seconds": 45
}
```

## Binary Size Comparison

| Implementation | Binary Size | Startup Time | Memory Usage |
|---------------|-------------|--------------|--------------|
| Python (with interpreter) | ~15 MB + interpreter | ~300ms | ~40 MB |
| Zig (ReleaseSmall) | ~200 KB | <1ms | ~2 MB |
| Zig (ReleaseFast) | ~250 KB | <1ms | ~2 MB |

**Key Advantages:**
- **~99% smaller** binary size
- **~300x faster** startup time
- **~20x lower** memory footprint
- No runtime dependencies (static binary)

## Performance Benefits

1. **Single Static Binary**: No dependencies, easy deployment
2. **Fast Startup**: Sub-millisecond cold starts
3. **Low Memory**: Perfect for containerized environments
4. **Native Performance**: Direct system calls, no interpreter overhead
5. **Cross-Compilation**: Build for any platform from any platform

## Cross-Compilation

Build for different platforms:

```bash
# Linux x86_64
zig build -Dtarget=x86_64-linux

# macOS ARM64
zig build -Dtarget=aarch64-macos

# Windows
zig build -Dtarget=x86_64-windows
```

## Testing

```bash
# Start the server
zig build run &

# Test endpoints
curl http://localhost:8080/
curl http://localhost:8080/health

# Test 404 handling
curl http://localhost:8080/nonexistent
```

## Project Structure

```
app_zig/
├── src/
│   ├── main.zig         # Main application & server
│   ├── models.zig       # Data structures (ServiceInfo, HealthResponse, etc.)
│   └── utils.zig        # Utility functions (hostname, uptime, timestamps)
├── docs/
│   ├── LAB01.md         # Implementation details
│   ├── ZIG.md           # Language justification
│   └── screenshots/     # Testing evidence
├── build.zig            # Build configuration
├── Makefile             # Build automation
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Why Zig?

- **Modern**: Clean syntax, strong type system
- **Fast**: Performance comparable to C
- **Safe**: Compile-time safety without runtime cost
- **Simple**: No hidden control flow, explicit allocations
- **Portable**: Cross-compile for any target
- **Small**: Tiny binaries perfect for containers

## Future Enhancements

- **Lab 2**: Multi-stage Docker builds (resulting in ~2MB images!)
- **Lab 9**: Extremely fast Kubernetes startup times
- Ideal for edge computing and resource-constrained environments

## License

Part of the DevOps Core Course - Lab 01 Bonus Task

## Author

Created for the DevOps Core Course - Lab 01 Bonus Task
