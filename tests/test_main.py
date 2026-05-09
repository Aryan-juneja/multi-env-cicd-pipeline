from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["message"] == "hello"


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_version_returns_expected_keys():
    r = client.get("/version")
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {"version", "git_sha", "environment"}
