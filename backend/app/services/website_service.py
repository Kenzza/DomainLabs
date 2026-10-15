import time
import urllib.parse
import httpx
from typing import Dict, Any, List, Optional
from app.core.security import validate_redirect, MAX_REDIRECTS, TIMEOUT_SECONDS, MAX_RESPONSE_BYTES, SecurityError

def inspect_website(validated_target: dict) -> Dict[str, Any]:
    current_url = validated_target["normalized_url"]
    redirect_chain = []
    redirect_count = 0

    start_time = time.time()

    try:
        with httpx.Client(timeout=TIMEOUT_SECONDS, verify=True, follow_redirects=False) as client:
            while redirect_count <= MAX_REDIRECTS:
                req_start = time.time()
                try:
                    with client.stream("GET", current_url) as response:
                        content_length = response.headers.get("content-length")
                        if content_length and int(content_length) > MAX_RESPONSE_BYTES:
                            return {
                                "status": "failed",
                                "data": None,
                                "message": "Response size exceeds maximum allowed limit (2 MiB)."
                            }

                        body_bytes = bytearray()
                        for chunk in response.iter_bytes(chunk_size=8192):
                            body_bytes.extend(chunk)
                            if len(body_bytes) > MAX_RESPONSE_BYTES:
                                return {
                                    "status": "failed",
                                    "data": None,
                                    "message": "Response body exceeded maximum allowed limit (2 MiB)."
                                }
                        
                        status_code = response.status_code
                        headers = response.headers
                        content_type = headers.get("content-type")
                        response_size = len(body_bytes)

                        # Handle redirects (301, 302, 303, 307, 308)
                        if status_code in (301, 302, 303, 307, 308):
                            location = headers.get("location")
                            if not location:
                                break
                            
                            next_url = urllib.parse.urljoin(current_url, location)
                            redirect_count += 1
                            if redirect_count > MAX_REDIRECTS:
                                return {
                                    "status": "failed",
                                    "data": {"redirect_chain": redirect_chain},
                                    "message": f"Maximum redirect limit ({MAX_REDIRECTS}) exceeded."
                                }

                            # Validate redirect target against SSRF & security policy
                            try:
                                validated_next = validate_redirect(current_url, next_url, redirect_count)
                            except SecurityError as se:
                                return {
                                    "status": "failed",
                                    "data": {"redirect_chain": redirect_chain},
                                    "message": f"Redirect target security validation failed: {str(se)}"
                                }

                            redirect_chain.append(current_url)
                            current_url = validated_next["normalized_url"]
                            continue
                        
                        # Non-redirect final response
                        total_elapsed_ms = (time.time() - start_time) * 1000.0
                        return {
                            "status": "success",
                            "data": {
                                "final_url": current_url,
                                "status_code": status_code,
                                "content_type": content_type,
                                "response_size_bytes": response_size,
                                "latency_ms": round(total_elapsed_ms, 2),
                                "redirect_chain": redirect_chain
                            },
                            "message": None
                        }

                except httpx.TimeoutException:
                    return {
                        "status": "timeout",
                        "data": None,
                        "message": "Website inspection request timed out."
                    }
                except httpx.RequestError as re:
                    return {
                        "status": "unavailable",
                        "data": None,
                        "message": f"Website inspection connection error: {str(re)}"
                    }

        return {
            "status": "failed",
            "data": {"redirect_chain": redirect_chain},
            "message": "Too many redirects."
        }

    except Exception as e:
        return {
            "status": "failed",
            "data": None,
            "message": f"Website inspection failed: {str(e)}"
        }
