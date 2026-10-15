import pytest
from unittest.mock import patch, MagicMock
import dns.resolver
import dns.exception
from app.services.dns_service import fetch_dns_intelligence

class MockRData:
    def __init__(self, value, preference=None, strings=None):
        self.value = value
        self.preference = preference
        self.strings = strings or [value.encode('utf-8')]

    def __str__(self):
        return self.value

class MockAnswer:
    def __init__(self, rdatas, ttl=300):
        self.rdatas = rdatas
        self.rrset = MagicMock()
        self.rrset.ttl = ttl

    def __iter__(self):
        return iter(self.rdatas)


@patch("dns.resolver.resolve")
def test_fetch_dns_success(mock_resolve):
    def side_effect(hostname, rdtype):
        if rdtype == "A":
            return MockAnswer([MockRData("93.184.216.34")])
        elif rdtype == "AAAA":
            return MockAnswer([MockRData("2606:2800:220:1:248:1893:25c8:1946")])
        elif rdtype == "MX":
            rdata = MockRData("mail.example.com")
            rdata.preference = 10
            rdata.exchange = MockRData("mail.example.com")
            return MockAnswer([rdata])
        elif rdtype == "NS":
            return MockAnswer([MockRData("ns1.example.com")])
        elif rdtype == "TXT":
            return MockAnswer([MockRData("v=spf1 include:_spf.example.com ~all", strings=[b"v=spf1 ", b"include:_spf.example.com"])])
        else:
            raise dns.resolver.NoAnswer()

    mock_resolve.side_effect = side_effect

    res = fetch_dns_intelligence("example.com")
    assert res["status"] == "success"
    records = res["data"]["records"]
    assert records["A"]["status"] == "success"
    assert records["A"]["items"][0]["value"] == "93.184.216.34"
    assert records["MX"]["items"][0]["preference"] == 10
    assert records["TXT"]["items"][0]["value"] == "v=spf1 include:_spf.example.com"


@patch("dns.resolver.resolve")
def test_fetch_dns_not_found(mock_resolve):
    mock_resolve.side_effect = dns.resolver.NXDOMAIN()

    res = fetch_dns_intelligence("nonexistent.example.com")
    assert res["status"] == "not_found"
    records = res["data"]["records"]
    assert records["A"]["status"] == "not_found"


@patch("dns.resolver.resolve")
def test_fetch_dns_timeout(mock_resolve):
    mock_resolve.side_effect = dns.exception.Timeout()

    res = fetch_dns_intelligence("timeout.example.com")
    assert res["status"] == "timeout"
    records = res["data"]["records"]
    assert records["A"]["status"] == "timeout"
