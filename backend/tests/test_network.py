import pytest
from unittest.mock import MagicMock, patch
from app.services.network_service import run_network_diagnostics

@patch("socket.getaddrinfo")
@patch("socket.create_connection")
@patch("ssl.create_default_context")
@patch("httpx.Client")
def test_network_diagnostics_success(mock_httpx_client_cls, mock_create_ctx, mock_create_conn, mock_getaddrinfo):
    mock_getaddrinfo.return_value = [(2, 1, 6, '', ('93.184.216.34', 443))]
    mock_sock = MagicMock()
    mock_create_conn.return_value = mock_sock

    mock_ctx = MagicMock()
    mock_ctx.wrap_socket.return_value.__enter__.return_value = MagicMock()
    mock_create_ctx.return_value = mock_ctx

    mock_client = MagicMock()
    mock_httpx_client_cls.return_value.__enter__.return_value = mock_client

    validated_target = {
        "input": "example.com",
        "normalized_host": "example.com",
        "normalized_url": "https://example.com"
    }

    res = run_network_diagnostics(validated_target)
    assert res["status"] == "success"
    assert res["data"]["dns_latency_ms"] is not None
    assert res["data"]["tcp_latency_ms"] is not None
    assert res["data"]["tls_latency_ms"] is not None
    assert res["data"]["http_latency_ms"] is not None
    assert res["data"]["total_duration_ms"] is not None

@patch("socket.getaddrinfo")
def test_network_diagnostics_timeout(mock_getaddrinfo):
    import socket
    mock_getaddrinfo.side_effect = socket.timeout("Timed out")

    validated_target = {
        "input": "example.com",
        "normalized_host": "example.com",
        "normalized_url": "https://example.com"
    }

    res = run_network_diagnostics(validated_target)
    assert res["status"] == "timeout"
