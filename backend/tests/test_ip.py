import pytest
from unittest.mock import MagicMock, patch
from app.services.ip_provider import BaseIPProvider, IpApiCoProvider
from app.services.ip_service import fetch_ip_intelligence

class MockIPProvider(BaseIPProvider):
    def __init__(self, response_dict):
        self.response_dict = response_dict

    def fetch_ip_info(self, ip_address: str):
        return self.response_dict

def test_ip_intelligence_success():
    mock_provider = MockIPProvider({
        "status": "success",
        "data": {
            "ip": "93.184.216.34",
            "asn": "AS15133",
            "organization": "EdgeCast Networks",
            "country": "United States",
            "region": "California",
            "city": "Los Angeles"
        },
        "message": None
    })

    res = fetch_ip_intelligence(["93.184.216.34"], provider=mock_provider)
    assert res["status"] == "success"
    assert len(res["data"]["ips"]) == 1
    assert res["data"]["ips"][0]["status"] == "success"
    assert res["data"]["ips"][0]["data"]["asn"] == "AS15133"

def test_ip_intelligence_timeout():
    mock_provider = MockIPProvider({
        "status": "timeout",
        "data": None,
        "message": "Timed out"
    })

    res = fetch_ip_intelligence(["93.184.216.34"], provider=mock_provider)
    assert res["status"] == "timeout"

def test_ip_intelligence_empty_ips():
    res = fetch_ip_intelligence([])
    assert res["status"] == "not_found"
