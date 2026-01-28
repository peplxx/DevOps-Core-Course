# Screenshots

This directory contains screenshots demonstrating the working application for Lab 01.

## Required Screenshots

1. **01-main-endpoint.png** - Main endpoint (`GET /`) showing complete JSON response
2. **02-health-check.png** - Health check endpoint (`GET /health`) response
3. **03-formatted-output.png** - Pretty-printed JSON output

## How to Take Screenshots

### Test the Main Endpoint
```bash
curl http://localhost:5000/ | python -m json.tool
```

### Test the Health Check
```bash
curl http://localhost:5000/health | python -m json.tool
```
