import ipaddress
import urllib.parse
import idna
import dns.resolver
from typing import List, Dict, Any, Optional

# Constants from docs/input-security-policy.md & technical-architecture.md
TIMEOUT_SECONDS = 10
MAX_RESPONSE_BYTES = 2 * 1024 * 1024  # 2 MiB
MAX_REDIRECTS = 5

class SecurityError(Exception):
    pass

class InvalidTargetError(SecurityError):
    pass

class UnsupportedSchemeError(SecurityError):
    pass

class CredentialsNotAllowedError(SecurityError):
    pass

class IPLiteralNotAllowedError(SecurityError):
    pass

class InvalidPortError(SecurityError):
    pass

class BlockedIPError(SecurityError):
    pass

class HostResolutionError(SecurityError):
    pass

class RedirectLimitExceededError(SecurityError):
    pass


def is_ip_blocked(ip_obj: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    # Handle NAT64 Well-Known Prefix 64:ff9b::/96 by evaluating the embedded IPv4 address
    nat64_prefix = ipaddress.ip_network("64:ff9b::/96")
    if isinstance(ip_obj, ipaddress.IPv6Address) and ip_obj in nat64_prefix:
        try:
            embedded_ipv4 = ipaddress.IPv4Address(ip_obj.packed[-4:])
            return is_ip_blocked(embedded_ipv4)
        except Exception:
            return True  # Fail closed if malformed embedding

    if (
        ip_obj.is_loopback
        or ip_obj.is_private
        or ip_obj.is_link_local
        or ip_obj.is_multicast
        or ip_obj.is_unspecified
        or ip_obj.is_reserved
    ):
        return True

    # Cloud metadata / specific sensitive ranges
    # AWS / Azure / GCP metadata IP: 169.254.169.254
    aws_metadata = ipaddress.ip_address("169.254.169.254")
    if ip_obj == aws_metadata:
        return True

    # Carrier-grade NAT: 100.64.0.0/10
    cg_nat = ipaddress.ip_network("100.64.0.0/10")
    if ip_obj in cg_nat:
        return True

    return False


def resolve_and_check_dns(hostname: str) -> List[str]:
    resolved_ips = []
    has_records = False

    # Resolve A records (IPv4)
    try:
        a_answers = dns.resolver.resolve(hostname, "A")
        has_records = True
        for rdata in a_answers:
            ip_str = rdata.address
            ip_obj = ipaddress.ip_address(ip_str)
            if is_ip_blocked(ip_obj):
                raise BlockedIPError(f"IP address {ip_str} resolved from {hostname} is blocked by SSRF policy.")
            resolved_ips.append(ip_str)
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.YXDOMAIN):
        pass
    except dns.exception.DNSException as e:
        pass

    # Resolve AAAA records (IPv6)
    try:
        aaaa_answers = dns.resolver.resolve(hostname, "AAAA")
        has_records = True
        for rdata in aaaa_answers:
            ip_str = rdata.address
            ip_obj = ipaddress.ip_address(ip_str)
            if is_ip_blocked(ip_obj):
                raise BlockedIPError(f"IP address {ip_str} resolved from {hostname} is blocked by SSRF policy.")
            resolved_ips.append(ip_str)
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.YXDOMAIN):
        pass
    except dns.exception.DNSException as e:
        pass

    if not has_records or not resolved_ips:
        raise HostResolutionError(f"Failed to resolve hostname {hostname} or no valid DNS records found.")

    return resolved_ips


def normalize_and_validate_target(target_input: str) -> Dict[str, Any]:
    if not target_input or not target_input.strip():
        raise InvalidTargetError("Target tidak boleh kosong.")

    raw_input = target_input.strip()

    # If no scheme provided, default to https:// (no automatic fallback to http)
    if "://" not in raw_input:
        full_url = f"https://{raw_input}"
    else:
        full_url = raw_input

    try:
        parsed = urllib.parse.urlparse(full_url)
    except Exception as e:
        raise InvalidTargetError(f"Format URL tidak valid: {e}")

    # Scheme check
    scheme = parsed.scheme.lower()
    if scheme not in ["http", "https"]:
        raise UnsupportedSchemeError(f"Skema protokol '{scheme}' tidak didukung. Hanya HTTP dan HTTPS yang diizinkan.")

    # Credentials check
    if parsed.username or parsed.password or "@" in parsed.netloc:
        raise CredentialsNotAllowedError("URL dengan username/password (credentials) tidak diizinkan.")

    hostname = parsed.hostname
    if not hostname:
        raise InvalidTargetError("Hostname tidak ditemukan dalam target.")

    # Remove trailing dot for check, but preserve/normalize
    hostname_clean = hostname.rstrip('.')

    # Check if hostname is an IP literal
    try:
        ipaddress.ip_address(hostname_clean)
        raise IPLiteralNotAllowedError("Input berupa alamat IP literal tidak diizinkan.")
    except ValueError:
        pass  # Not an IP literal, good.

    # Port policy check
    port = parsed.port
    if scheme == "http":
        if port is not None and port != 80:
            raise InvalidPortError(f"Port {port} tidak diizinkan untuk HTTP (hanya port 80).")
        effective_port = 80
    else:  # https
        if port is not None and port != 443:
            raise InvalidPortError(f"Port {port} tidak diizinkan untuk HTTPS (hanya port 443).")
        effective_port = 443

    # IDN / Punycode normalization
    try:
        punycode_host = idna.encode(hostname_clean).decode('ascii')
    except Exception as e:
        raise InvalidTargetError(f"Gagal melakukan normalisasi IDN/Punycode untuk hostname '{hostname}': {e}")

    # DNS resolution and SSRF IP check
    resolved_ips = resolve_and_check_dns(punycode_host)

    # Reconstruct normalized URL without fragment
    netloc_normalized = punycode_host
    if port is not None:
        netloc_normalized = f"{punycode_host}:{port}"

    normalized_url = urllib.parse.urlunparse((
        scheme,
        netloc_normalized,
        parsed.path if parsed.path else "",
        parsed.params,
        parsed.query,
        ""  # fragment discarded/ignored per policy
    ))

    return {
        "input": raw_input,
        "normalized_host": punycode_host,
        "normalized_url": normalized_url,
        "scheme": scheme,
        "port": effective_port,
        "resolved_ips": resolved_ips
    }


def validate_redirect(original_url: str, redirect_url: str, redirect_count: int) -> Dict[str, Any]:
    if redirect_count >= MAX_REDIRECTS:
        raise RedirectLimitExceededError(f"Batas maksimum redirect ({MAX_REDIRECTS}) terlampaui.")
    
    return normalize_and_validate_target(redirect_url)
