from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("app.core.security.resolve_and_check_dns", return_value=["93.184.216.34"])
@patch("app.services.analyzer_service.fetch_dns_intelligence", return_value={"status": "success", "data": {"records": {}}, "message": None})
def test_analyze_valid_request(mock_dns_fetch, mock_sec_dns):
    response = client.post(
        "/api/v1/analyze",
        json={
            "target": "example.com",
            "checks": ["dns", "ip"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "target" in data
    assert data["target"]["normalized_host"] == "example.com"
    assert "dns" in data["checks"]
    assert "ip" in data["checks"]
    assert data["checks"]["dns"]["status"] == "success"

def test_analyze_missing_target():
    response = client.post(
        "/api/v1/analyze",
        json={
            "checks": ["dns"]
        }
    )
    assert response.status_code == 422

def test_analyze_empty_target():
    response = client.post(
        "/api/v1/analyze",
        json={
            "target": "   ",
            "checks": ["dns"]
        }
    )
    assert response.status_code == 422
