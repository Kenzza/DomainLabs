import pytest
from unittest.mock import MagicMock, patch
from app.services.website_service import inspect_website

class MockResponse:
    def __init__(self, status_code, headers, content_bytes):
        self.status_code = status_code
        self.headers = headers
        self.content_bytes = content_bytes

    def iter_bytes(self, chunk_size=8192):
        for i in range(0, len(self.content_bytes), chunk_size):
            yield self.content_bytes[i:i+chunk_size]

class MockContextManager:
    def __init__(self, response):
        self.response = response

    def __enter__(self):
        return self.response

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

@patch("httpx.Client")
def test_inspect_website_success(mock_client_cls):
    mock_client = MagicMock()
    mock_response = MockResponse(
        status_code=200,
        headers={"content-type": "text/html", "content-length": "12"},
        content_bytes=b"Hello World!"
    )
    mock_client.stream.return_value = MockContextManager(mock_response)
    mock_client_cls.return_value.__enter__.return_value = mock_client

    validated_target = {
        "input": "example.com",
        "normalized_host": "example.com",
        "normalized_url": "https://example.com"
    }

    res = inspect_website(validated_target)
    assert res["status"] == "success"
    assert res["data"]["status_code"] == 200
    assert res["data"]["response_size_bytes"] == 12
    assert res["data"]["final_url"] == "https://example.com"

@patch("httpx.Client")
def test_inspect_website_timeout(mock_client_cls):
    import httpx
    mock_client = MagicMock()
    mock_client.stream.side_effect = httpx.TimeoutException("Timed out")
    mock_client_cls.return_value.__enter__.return_value = mock_client

    validated_target = {
        "input": "example.com",
        "normalized_host": "example.com",
        "normalized_url": "https://example.com"
    }

    res = inspect_website(validated_target)
    assert res["status"] == "timeout"
