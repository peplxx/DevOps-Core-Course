def test_root_success(client):
    resp = client.get("/")
    assert resp.status_code == 200

    data = resp.json()
    assert set(data.keys()) == {"service", "system", "runtime", "request", "endpoints"}

    # Service info contract
    assert set(data["service"].keys()) == {"name", "version", "description", "framework"}
    assert isinstance(data["service"]["name"], str) and data["service"]["name"]
    assert isinstance(data["service"]["version"], str) and data["service"]["version"]
    assert data["service"]["framework"] == "FastAPI"

    # System info contract (values vary per environment, so only validate shape/types)
    assert "hostname" in data["system"]
    assert "platform" in data["system"]
    assert "architecture" in data["system"]
    assert "cpu_count" in data["system"]
    assert "python_version" in data["system"]

    # Runtime info contract
    assert set(data["runtime"].keys()) == {
        "uptime_seconds",
        "uptime_human",
        "current_time",
        "timezone",
    }
    assert isinstance(data["runtime"]["uptime_seconds"], int)
    assert data["runtime"]["uptime_seconds"] >= 0
    assert data["runtime"]["timezone"] == "UTC"

    # Request info contract
    assert set(data["request"].keys()) == {"client_ip", "user_agent", "method", "path"}
    assert data["request"]["method"] == "GET"
    assert data["request"]["path"] == "/"

    # Endpoints list contract
    assert isinstance(data["endpoints"], list)
    assert {"path": "/", "method": "GET", "description": "Service information"} in data["endpoints"]
    assert {"path": "/visits", "method": "GET", "description": "Persisted visit counter"} \
           in data["endpoints"]
    assert {"path": "/health", "method": "GET", "description": "Health check"} in data["endpoints"]


def test_health_success(client):
    resp = client.get("/health")
    assert resp.status_code == 200

    data = resp.json()
    assert set(data.keys()) == {"status", "timestamp", "uptime_seconds"}
    assert data["status"] == "healthy"
    assert isinstance(data["timestamp"], str) and data["timestamp"]
    assert isinstance(data["uptime_seconds"], int)
    assert data["uptime_seconds"] >= 0


def test_404_error_contract(client):
    resp = client.get("/does-not-exist")
    assert resp.status_code == 404
    assert resp.json() == {"error": "Not Found", "message": "Endpoint does not exist"}


def test_405_method_not_allowed(client):
    resp = client.post("/health")
    assert resp.status_code == 405


def test_visits_counter(client):
    assert client.get("/visits").json() == {"visits": 0}
    client.get("/")
    client.get("/")
    assert client.get("/visits").json() == {"visits": 2}

