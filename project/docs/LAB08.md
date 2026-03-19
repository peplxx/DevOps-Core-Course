# Lab 08 — Metrics & Monitoring with Prometheus

## 1. Architecture

```
┌─────────────┐    scrape /metrics     ┌──────────────┐    query PromQL    ┌─────────────┐
│  app-python  │ ◄──────────────────── │  Prometheus   │ ◄──────────────── │   Grafana    │
│  :5000       │                        │  :9090        │                    │  :3000       │
└─────────────┘                        └──────────────┘                    └─────────────┘
       │                                   │  ▲                                │
       │ logs                              │  │ self-scrape                    │
       ▼                                   │  └─────────────                   │
┌─────────────┐                            │                                   │
│  Promtail   │ ──push──► ┌──────────┐    │ scrape /metrics                   │
│             │           │   Loki   │ ◄──┘                                   │
└─────────────┘           │  :3100   │ ◄──────── query LogQL ─────────────────┘
                          └──────────┘
```

**Data Flow:**
- **Metrics path:** App exposes `/metrics` → Prometheus scrapes every 15s → Grafana visualizes via PromQL
- **Logs path (Lab 7):** App writes JSON logs → Promtail ships to Loki → Grafana queries via LogQL
- Prometheus also scrapes its own metrics, Loki metrics, and Grafana metrics

## 2. Application Instrumentation

### Metric Definitions

| Metric | Type | Labels | Purpose |
|--------|------|--------|---------|
| `http_requests_total` | Counter | `method`, `endpoint`, `status` | Total HTTP requests (RED: Rate) |
| `http_request_duration_seconds` | Histogram | `method`, `endpoint` | Request latency distribution (RED: Duration) |
| `http_requests_in_progress` | Gauge | — | Concurrent request count |
| `devops_info_endpoint_calls` | Counter | `endpoint` | Business-level endpoint usage tracking |
| `devops_info_system_collection_seconds` | Histogram | — | System info collection performance |

### Why These Metrics

Following the **RED Method** for request-driven services:
- **Rate** — `http_requests_total` tracks throughput per endpoint
- **Errors** — Same counter filtered by `status=~"5.."` gives error rate
- **Duration** — `http_request_duration_seconds` histogram provides p50/p95/p99 latencies

The **Gauge** (`http_requests_in_progress`) shows current load — useful for spotting saturation.

### Implementation

Metrics are defined in `app/metrics.py` and recorded via FastAPI middleware in `app/app.py`:
- Middleware intercepts all requests (except `/metrics` itself)
- Increments in-progress gauge on entry, decrements in `finally` block
- Records counter + histogram after response

## 3. Prometheus Configuration

**File:** `monitoring/prometheus/prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "prometheus"   # Self-monitoring
    targets: ["localhost:9090"]

  - job_name: "app"          # Python application
    targets: ["app-python:5000"]
    metrics_path: "/metrics"

  - job_name: "loki"         # Log aggregator
    targets: ["loki:3100"]

  - job_name: "grafana"      # Visualization
    targets: ["grafana:3000"]
```

**Retention:**
- Time-based: 15 days (`--storage.tsdb.retention.time=15d`)
- Size-based: 10 GB (`--storage.tsdb.retention.size=10GB`)

## 4. Dashboard Walkthrough

The provisioned dashboard (`DevOps App - Metrics (RED Method)`) contains 7 panels:

| # | Panel | Type | PromQL Query | Purpose |
|---|-------|------|-------------|---------|
| 1 | Service Uptime | Stat | `up{job="app"}` | Shows UP/DOWN status |
| 2 | Request Rate | Time series | `sum(rate(http_requests_total[5m])) by (endpoint)` | Requests/sec per endpoint |
| 3 | Error Rate | Time series | `sum(rate(http_requests_total{status=~"5.."}[5m]))` | 5xx errors/sec |
| 4 | Request Duration p95 | Time series | `histogram_quantile(0.95, sum(rate(..._bucket[5m])) by (le, endpoint))` | 95th percentile latency |
| 5 | Duration Heatmap | Heatmap | `sum(increase(..._bucket[5m])) by (le)` | Latency distribution |
| 6 | Active Requests | Time series | `http_requests_in_progress` | Current concurrency |
| 7 | Status Code Dist. | Pie chart | `sum by (status) (increase(http_requests_total[1h]))` | 2xx/4xx/5xx breakdown |

## 5. PromQL Examples

```promql
# 1. Overall request rate across all endpoints
sum(rate(http_requests_total[5m]))

# 2. Error percentage (5xx / total * 100)
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100

# 3. 95th percentile latency per endpoint
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint))

# 4. Top endpoints by request volume
topk(5, sum by (endpoint) (rate(http_requests_total[5m])))

# 5. Services that are down
up == 0

# 6. Average request duration
sum(rate(http_request_duration_seconds_sum[5m])) / sum(rate(http_request_duration_seconds_count[5m]))

# 7. Request rate by status code
sum by (status) (rate(http_requests_total[5m]))
```

## 6. Production Setup

### Health Checks

| Service | Health Endpoint | Interval | Retries |
|---------|----------------|----------|---------|
| Loki | `GET /ready` | 10s | 5 |
| Promtail | `GET /ready` | 10s | 5 |
| Prometheus | `GET /-/healthy` | 10s | 5 |
| Grafana | `GET /api/health` | 10s | 5 |
| app-python | `GET /health` | 10s | 5 |

### Resource Limits

| Service | CPU Limit | Memory Limit | CPU Reserved | Memory Reserved |
|---------|-----------|-------------|-------------|-----------------|
| Prometheus | 1.0 | 1 GB | 0.5 | 512 MB |
| Loki | 1.0 | 1 GB | 0.5 | 512 MB |
| Grafana | 0.5 | 512 MB | 0.25 | 256 MB |
| Promtail | 0.5 | 512 MB | 0.25 | 256 MB |
| app-python | 0.5 | 256 MB | 0.25 | 128 MB |

### Retention Policies

- **Prometheus:** 15 days / 10 GB (whichever is reached first)
- **Loki:** 168h (7 days) for old sample rejection

### Persistent Volumes

| Volume | Mounted To | Purpose |
|--------|-----------|---------|
| `prometheus-data` | `/prometheus` | TSDB time-series storage |
| `loki-data` | `/loki` | Chunks, index, compactor |
| `grafana-data` | `/var/lib/grafana` | Dashboards, users, settings |

## 7. Metrics vs Logs — When to Use Each

| Aspect | Metrics (Prometheus) | Logs (Loki) |
|--------|---------------------|-------------|
| Question answered | "How much / how often?" | "What happened?" |
| Data type | Numeric time-series | Unstructured/structured text |
| Cardinality | Low (labels) | High (free-form) |
| Storage cost | Compact | Larger |
| Best for | Alerting, dashboards, SLOs | Debugging, auditing, tracing |
| Query language | PromQL | LogQL |
| Example | "Error rate > 5% for 5 min" | "Show me the stack trace for request X" |

**Use together:** Metrics alert you to problems; logs help you diagnose them.

## 8. Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| `/metrics` endpoint being tracked by its own middleware | Skip metrics path in the middleware to avoid recursion |
| Histogram bucket selection | Used default Prometheus buckets optimized for web request latencies |
| Grafana datasource manual setup | Automated via provisioning YAML mounted into Grafana container |
| Dashboard persistence across restarts | Used Grafana provisioning + named Docker volume |
