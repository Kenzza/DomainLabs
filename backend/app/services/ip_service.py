from typing import List, Dict, Any, Optional
from app.services.ip_provider import BaseIPProvider, IpApiCoProvider

def fetch_ip_intelligence(resolved_ips: List[str], provider: Optional[BaseIPProvider] = None) -> Dict[str, Any]:
    if not resolved_ips:
        return {
            "status": "not_found",
            "data": {"ips": []},
            "message": "No IP addresses provided for IP Intelligence."
        }

    if provider is None:
        provider = IpApiCoProvider()

    results = []
    has_success = False
    has_timeout = False
    has_unavailable = False
    has_failed = False

    # Limit to max 3 IPs to avoid excessive provider calls
    target_ips = resolved_ips[:3]

    for ip in target_ips:
        res = provider.fetch_ip_info(ip)
        results.append({
            "ip": ip,
            "status": res["status"],
            "data": res["data"],
            "message": res["message"]
        })
        if res["status"] == "success":
            has_success = True
        elif res["status"] == "timeout":
            has_timeout = True
        elif res["status"] == "unavailable":
            has_unavailable = True
        elif res["status"] == "failed":
            has_failed = True

    if has_success:
        overall_status = "success"
    elif has_timeout:
        overall_status = "timeout"
    elif has_unavailable:
        overall_status = "unavailable"
    elif has_failed:
        overall_status = "failed"
    else:
        overall_status = "not_found"

    return {
        "status": overall_status,
        "data": {
            "ips": results
        },
        "message": None if has_success else "IP Intelligence lookups failed or timed out."
    }
