def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert body["app_name"] == "crypto-research-agent"
    assert "app_version" in body
    assert body["trading_mode"] == "research_only"


def test_readiness_returns_status(client):
    response = client.get("/readiness")
    assert response.status_code == 200

    body = response.json()
    assert body["status"] in ("ok", "degraded")
    assert "database" in body["checks"]
    assert "cache" in body["checks"]
