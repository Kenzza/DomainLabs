from datetime import datetime, timezone
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse, TargetInfo, ModuleResult
from app.services.dns_service import fetch_dns_intelligence
from app.services.ip_service import fetch_ip_intelligence
from app.services.website_service import inspect_website
from app.services.tls_service import inspect_tls
from app.services.network_service import run_network_diagnostics

def run_analysis(request: AnalyzeRequest, validated_target: dict) -> AnalyzeResponse:
    now_str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    checks_result = {}
    requested_checks = request.checks or ["dns", "ip", "http", "tls"]
    normalized_host = validated_target["normalized_host"]
    resolved_ips = validated_target.get("resolved_ips", [])

    for check in requested_checks:
        if check == "dns":
            dns_res = fetch_dns_intelligence(normalized_host)
            checks_result["dns"] = ModuleResult(
                status=dns_res["status"],
                data=dns_res["data"],
                message=dns_res["message"]
            )
        elif check == "ip":
            ip_res = fetch_ip_intelligence(resolved_ips)
            checks_result["ip"] = ModuleResult(
                status=ip_res["status"],
                data=ip_res["data"],
                message=ip_res["message"]
            )
        elif check in ("http", "website"):
            web_res = inspect_website(validated_target)
            checks_result[check] = ModuleResult(
                status=web_res["status"],
                data=web_res["data"],
                message=web_res["message"]
            )
        elif check == "tls":
            tls_res = inspect_tls(validated_target)
            checks_result["tls"] = ModuleResult(
                status=tls_res["status"],
                data=tls_res["data"],
                message=tls_res["message"]
            )
        elif check in ("network", "diagnostics", "latency"):
            net_res = run_network_diagnostics(validated_target)
            checks_result[check] = ModuleResult(
                status=net_res["status"],
                data=net_res["data"],
                message=net_res["message"]
            )
        else:
            checks_result[check] = ModuleResult(
                status="unavailable",
                data=None,
                message=f"Modul {check} belum diimplementasikan pada Phase 1G (stub)."
            )

    return AnalyzeResponse(
        target=TargetInfo(
            input=validated_target["input"],
            normalized_host=validated_target["normalized_host"],
            normalized_url=validated_target["normalized_url"]
        ),
        started_at=now_str,
        completed_at=now_str,
        checks=checks_result
    )
