from fastapi.testclient import TestClient
from incident.main import app


def test_liveness_and_readiness_endpoints():
    with TestClient(app) as client:
        assert client.get("/healthz").status_code == 200
        assert client.get("/healthz").json() == {"status": "ok"}
        assert client.get("/v1/readyz").status_code == 200
