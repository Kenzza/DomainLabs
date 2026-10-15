import httpx
from typing import Dict, Any, Optional

class BaseIPProvider:
    def fetch_ip_info(self, ip_address: str) -> Dict[str, Any]:
        raise NotImplementedError

class IpApiCoProvider(BaseIPProvider):
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.base_url = "https://ipapi.co"

    def fetch_ip_info(self, ip_address: str) -> Dict[str, Any]:
        url = f"{self.base_url}/{ip_address}/json/"
        try:
            with httpx.Client(timeout=self.timeout, verify=True, follow_redirects=False) as client:
                response = client.get(url, headers={"User-Agent": "DomainLens/1.0"})
                
                if response.status_code == 404:
                    return {"status": "not_found", "data": None, "message": "IP info not found."}
                if response.status_code == 429:
                    return {"status": "unavailable", "data": None, "message": "IP Intelligence provider rate limited."}
                if response.status_code >= 500:
                    return {"status": "unavailable", "data": None, "message": f"IP Intelligence provider server error ({response.status_code})."}
                if response.status_code >= 400:
                    return {"status": "failed", "data": None, "message": f"IP Intelligence provider client error ({response.status_code})."}
                
                try:
                    data = response.json()
                except Exception:
                    return {"status": "failed", "data": None, "message": "Invalid JSON response from IP Intelligence provider."}

                if isinstance(data, dict) and data.get("error"):
                    return {"status": "failed", "data": None, "message": data.get("reason", "Provider error")}
                
                normalized = {
                    "ip": data.get("ip", ip_address),
                    "asn": data.get("asn"),
                    "organization": data.get("org"),
                    "country": data.get("country_name"),
                    "region": data.get("region"),
                    "city": data.get("city"),
                }
                return {"status": "success", "data": normalized, "message": None}

        except httpx.TimeoutException:
            return {"status": "timeout", "data": None, "message": "IP Intelligence provider request timed out."}
        except httpx.RequestError as e:
            return {"status": "failed", "data": None, "message": f"IP Intelligence request error: {str(e)}"}
        except Exception as e:
            return {"status": "failed", "data": None, "message": f"IP Intelligence unexpected error: {str(e)}"}
