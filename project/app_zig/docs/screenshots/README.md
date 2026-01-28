# Screenshots - Zig Implementation

This directory contains screenshots demonstrating the Zig implementation for Lab 01 Bonus Task.

## Required Screenshots

1. **01-build-output.png** - Compilation output showing binary size
2. **02-main-endpoint.png** - Main endpoint (`GET /`) JSON response
3. **03-health-check.png** - Health check response
4. **04-binary-comparison.png** - Size comparison: Zig vs Python

## How to Take Screenshots

### Build the Application
```bash
# Build optimized version
make release

# Check binary size
ls -lh zig-out/bin/devops-info-service
```

### Run and Test
```bash
# Start the server
./zig-out/bin/devops-info-service &

# Test main endpoint
curl http://localhost:8080/ | python -m json.tool

# Test health check
curl http://localhost:8080/health | python -m json.tool

# Show size comparison
du -h zig-out/bin/devops-info-service
du -h ../app_python/  # Compare with Python
```

### Binary Size Comparison
```bash
# Zig binary
ls -lh zig-out/bin/devops-info-service

# Python equivalent (interpreter + packages)
du -sh $(which python3)
du -sh ../app_python/venv/
```

## Screenshot Guidelines

- Use full terminal window
- Ensure text is readable
- Show commands and output
- Include timestamps where visible
- Save as PNG format
