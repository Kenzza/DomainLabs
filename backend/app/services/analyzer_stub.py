from datetime import datetime, timezone
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse, TargetInfo, ModuleResult

def run_analysis_stub(request: AnalyzeRequest, validated_target: dict) -> AnalyzeResponse:
    now_str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    checks_result = {}
    requested_checks = request.checks or ["dns", "ip", "http", "tls"]

    for check in requested_checks:
        checks_result[check] = ModuleResult(
            status="unavailable",
            data=None,
            message=f"Modul {check} belum diimplementasikan pada Phase 1A (stub)."
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
