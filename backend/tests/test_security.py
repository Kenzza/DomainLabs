import pytest
import ipaddress
from unittest.mock import patch
from app.core.security import (
    normalize_and_validate_target,
    validate_redirect,
    is_ip_blocked,
    InvalidTargetError,
    UnsupportedSchemeError,
    CredentialsNotAllowedError,
    IPLiteralNotAllowedError,
    InvalidPortError,
    BlockedIPError,
    RedirectLimitExceededError
)

@patch("app.core.security.resolve_and_check_dns", return_value=["93.184.216.34"])
def test_normalize_valid_domain(mock_dns):
    res = normalize_and_validate_target("example.com")
    assert res["scheme"] == "https"
    assert res["normalized_host"] == "example.com"
    assert res["normalized_url"] == "https://example.com"
    assert res["resolved_ips"] == ["93.184.216.34"]

@patch("app.core.security.resolve_and_check_dns", return_value=["93.184.216.34"])
def test_normalize_valid_url_http(mock_dns):
    res = normalize_and_validate_target("http://example.com")
    assert res["scheme"] == "http"
    assert res["port"] == 80
    assert res["normalized_host"] == "example.com"

@patch("app.core.security.resolve_and_check_dns", return_value=["93.184.216.34"])
def test_normalize_valid_url_https_port(mock_dns):
    res = normalize_and_validate_target("https://example.com:443")
    assert res["scheme"] == "https"
    assert res["port"] == 443

@patch("app.core.security.resolve_and_check_dns", return_value=["93.184.216.34"])
def test_trailing_dot(mock_dns):
    res = normalize_and_validate_target("example.com.")
    assert res["normalized_host"] == "example.com"

@patch("app.core.security.resolve_and_check_dns", return_value=["93.184.216.34"])
def test_idn_normalization(mock_dns):
    res = normalize_and_validate_target("xn--mnchen-3ya.de")
    assert res["normalized_host"] == "xn--mnchen-3ya.de"

def test_invalid_empty():
    with pytest.raises(InvalidTargetError):
        normalize_and_validate_target("")

def test_unsupported_scheme():
    with pytest.raises(UnsupportedSchemeError):
        normalize_and_validate_target("ftp://example.com")

def test_credentials_not_allowed():
    with pytest.raises(CredentialsNotAllowedError):
        normalize_and_validate_target("https://user:pass@example.com")

def test_ip_literal_ipv4():
    with pytest.raises(IPLiteralNotAllowedError):
        normalize_and_validate_target("8.8.8.8")

def test_ip_literal_ipv6():
    with pytest.raises(IPLiteralNotAllowedError):
        normalize_and_validate_target("[2001:4860:4860::8888]")

def test_invalid_port_http():
    with pytest.raises(InvalidPortError):
        normalize_and_validate_target("http://example.com:8080")

def test_invalid_port_https():
    with pytest.raises(InvalidPortError):
        normalize_and_validate_target("https://example.com:8443")

@patch("app.core.security.resolve_and_check_dns", side_effect=BlockedIPError("Blocked IP"))
def test_blocked_loopback_domain(mock_dns):
    # localhost resolves to 127.0.0.1 or ::1
    with pytest.raises(BlockedIPError):
        normalize_and_validate_target("localhost")

@patch("app.core.security.resolve_and_check_dns", return_value=["64:ff9b::a29f:80e9"]) # public embedded IPv4 162.159.128.233
def test_nat64_public_allowed(mock_dns):
    res = normalize_and_validate_target("discord.com")
    assert res["resolved_ips"] == ["64:ff9b::a29f:80e9"]

def test_is_ip_blocked_nat64():
    assert is_ip_blocked(ipaddress.ip_address("64:ff9b::a29f:80e9")) == False # public
    assert is_ip_blocked(ipaddress.ip_address("64:ff9b::7f00:0001")) == True  # loopback
    assert is_ip_blocked(ipaddress.ip_address("64:ff9b::a9fe:a9fe")) == True  # metadata
    assert is_ip_blocked(ipaddress.ip_address("64:ff9b::6440:0001")) == True  # CGNAT

def test_validate_redirect_limit():
    with pytest.raises(RedirectLimitExceededError):
        validate_redirect("https://example.com", "https://example.com/redirect", 5)
