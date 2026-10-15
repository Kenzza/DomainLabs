import ssl
import socket
import urllib.parse
from typing import Dict, Any, Optional
from app.core.security import TIMEOUT_SECONDS

def inspect_tls(validated_target: dict) -> Dict[str, Any]:
    url = validated_target["normalized_url"]
    parsed = urllib.parse.urlparse(url)
    
    if parsed.scheme != "https":
        return {
            "status": "unavailable",
            "data": None,
            "message": "TLS certificate intelligence is only supported for HTTPS targets."
        }
    
    hostname = parsed.hostname
    port = parsed.port or 443
    if port != 443:
        return {
            "status": "failed",
            "data": None,
            "message": f"Invalid port {port} for TLS inspection (only port 443 allowed)."
        }

    context = ssl.create_default_context()
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED

    try:
        with socket.create_connection((hostname, port), timeout=TIMEOUT_SECONDS) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                version = ssock.version()

                subject = dict(x[0] for x in cert.get("subject", ()))
                issuer = dict(x[0] for x in cert.get("issuer", ()))
                not_before = cert.get("notBefore")
                not_after = cert.get("notAfter")
                san = [x[1] for x in cert.get("subjectAltName", ()) if x[0] == "DNS"]

                return {
                    "status": "success",
                    "data": {
                        "subject": subject,
                        "issuer": issuer,
                        "not_before": not_before,
                        "not_after": not_after,
                        "subject_alternative_names": san,
                        "tls_version": version,
                        "cipher": cipher[0] if cipher else None
                    },
                    "message": None
                }

    except socket.timeout:
        return {
            "status": "timeout",
            "data": None,
            "message": "TLS handshake connection timed out."
        }
    except ssl.SSLCertVerificationError as ce:
        return {
            "status": "failed",
            "data": None,
            "message": f"TLS certificate verification failed: {str(ce)}"
        }
    except ssl.SSLError as se:
        return {
            "status": "failed",
            "data": None,
            "message": f"TLS handshake SSL error: {str(se)}"
        }
    except socket.error as se:
        return {
            "status": "unavailable",
            "data": None,
            "message": f"TLS socket connection error: {str(se)}"
        }
    except Exception as e:
        return {
            "status": "failed",
            "data": None,
            "message": f"TLS inspection failed: {str(e)}"
        }
