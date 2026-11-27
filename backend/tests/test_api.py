from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    assert client.get("/health").json()["status"] == "ok"


def test_contract() -> None:
    body = client.get("/contract").json()
    assert "person_4" in body["ownership"]


def test_demo_synthetic() -> None:
    resp = client.post("/demo/synthetic")
    assert resp.status_code == 200
    assert resp.json()["row_count"] == 6
