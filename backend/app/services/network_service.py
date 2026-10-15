import time
import socket
import ssl
import urllib.parse
import httpx
from typing import Dict, Any, Optional
from app.core.security import TIMEOUT_SECONDS

def run_network_diagnostics(validated_target: dict) -> Dict[str, Any]:
    url = validated_target["normalized_url"]
    parsed = urllib.parse.urlparse(url)
    hostname = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    is_https = (parsed.scheme == "https")

    metrics = {
        "dns_latency_ms": None,
        "tcp_latency_ms": None,
        "tls_latency_ms": None,
        "http_latency_ms": None,
        "total_duration_ms": None
    }

    start_total = time.time()

    try:
        # 1. DNS Timing
        t0 = time.time()
        addr_info = socket.getaddrinfo(hostname, port, proto=socket.IPPROTO_TCP)
        dns_ms = (time.time() - t0) * 1000.0
        metrics["dns_latency_ms"] = round(dns_ms, 2)
        
        target_ip = addr_info[0][4][0]

        # 2. TCP Timing
        t0 = time.time()
        sock = socket.create_connection((target_ip, port), timeout=TIMEOUT_SECONDS)
        tcp_ms = (time.time() - t0) * 1000.0
        metrics["tcp_latency_ms"] = round(tcp_ms, 2)

        try:
            if is_https:
                context = ssl.create_default_context()
                t0 = time.time()
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    pass
                tls_ms = (time.time() - t0) * 1000.0
                metrics["tls_latency_ms"] = round(tls_ms, 2)
        finally:
            try:
                sock.close()
            except Exception:
                pass

        # 3. HTTP Timing
        t0 = time.time()
        with httpx.Client(timeout=TIMEOUT_SECONDS, verify=True, follow_redirects=False) as client:
            client.get(url)
        http_ms = (time.time() - t0) * 1000.0
        metrics["http_latency_ms"] = round(http_ms, 2)

        total_ms = (time.time() - start_total) * 1000.0
        metrics["total_duration_ms"] = round(total_ms, 2)

        return {
            "status": "success",
            "data": metrics,
            "message": None
        }

    except socket.timeout:
        return {
            "status": "timeout",
            "data": metrics,
            "message": "Network diagnostics timed out."
        }
    except (socket.error, httpx.RequestError) as se:
        return {
            "status": "unavailable",
            "data": metrics,
            "message": f"Network diagnostics connection error: {str(se)}"
        }
    except Exception as e:
        return {
            "status": "failed",
            "data": metrics,
            "message": f"Network diagnostics failed: {str(e)}"
        }
