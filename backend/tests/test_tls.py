import pytest
from unittest.mock import MagicMock, patch
from app.services.tls_service import inspect_tls

@patch("ssl.create_default_context")
@patch("socket.create_connection")
def test_inspect_tls_success(mock_create_conn, mock_create_ctx):
    mock_sock = MagicMock()
    mock_create_conn.return_value = mock_sock

    mock_ssock = MagicMock()
    mock_ssock.getpeercert.return_value = {
        "subject": ((("commonName", "example.com"),),),
        "issuer": ((("commonName", "Test CA"),),),
        "notBefore": "Jan  1 00:00:00 2026 GMT",
        "notAfter": "Dec 31 23:59:59 2026 GMT",
        "subjectAltName": (("DNS", "example.com"), ("DNS", "www.example.com"))
    }
    mock_ssock.cipher.return_value = ("TLS_AES_256_GCM_SHA384", "TLSv1.3", 256)
    mock_ssock.version.return_value = "TLSv1.3"

    mock_ctx = MagicMock()
    mock_ctx.wrap_socket.return_value.__enter__.return_value = mock_ssock
    mock_create_ctx.return_value = mock_ctx

    validated_target = {
        "input": "example.com",
        "normalized_host": "example.com",
        "normalized_url": "https://example.com"
    }

    res = inspect_tls(validated_target)
    assert res["status"] == "success"
    assert res["data"]["subject"]["commonName"] == "example.com"
    assert res["data"]["issuer"]["commonName"] == "Test CA"
    assert res["data"]["tls_version"] == "TLSv1.3"
    assert "example.com" in res["data"]["subject_alternative_names"]

def test_inspect_tls_non_https():
    validated_target = {
        "input": "http://example.com",
        "normalized_host": "example.com",
        "normalized_url": "http://example.com"
    }

    res = inspect_tls(validated_target)
    assert res["status"] == "unavailable"
