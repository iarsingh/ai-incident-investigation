from fastapi.testclient import TestClient

from incident.main import app

client = TestClient(app)


def test_memory_evidence_is_a_hypothesis_not_a_confirmed_cause():
    body = client.post("/investigations", json={"service": "billing", "oom_killed": True, "memory_percent": 94, "restart_count": 4}).json()
    assert body["confirmed_root_cause"] is False
    assert body["hypotheses"][0]["id"] == "memory-limit"
    quiet = client.post("/investigations", json={"service": "billing"}).json()
    assert quiet["hypotheses"] == []
