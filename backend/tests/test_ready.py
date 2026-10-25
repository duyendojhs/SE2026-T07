from fastapi.testclient import TestClient

from app.api import health


def test_ready_checks_database_and_redis(
    client: TestClient, monkeypatch: object
) -> None:
    monkeypatch.setattr(health, "ping_redis", lambda: None)  # type: ignore[attr-defined]

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok", "redis": "ok"}


def test_ready_reports_redis_failure(client: TestClient, monkeypatch: object) -> None:
    def fail() -> None:
        raise RuntimeError("redis down")

    monkeypatch.setattr(health, "ping_redis", fail)  # type: ignore[attr-defined]

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json()["detail"] == "redis unavailable"
