import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch) -> TestClient:
    """Use a temp visits file so tests do not require /data."""
    monkeypatch.setenv("VISITS_FILE", str(tmp_path / "visits"))
    from app.app import app

    return TestClient(app)

