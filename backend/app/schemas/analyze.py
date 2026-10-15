from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    target: str = Field(..., description="Domain or full URL to analyze")
    checks: Optional[List[str]] = Field(
        default=["dns", "ip", "http", "tls"],
        description="List of checks to perform"
    )

class TargetInfo(BaseModel):
    input: str
    normalized_host: str
    normalized_url: str

class ModuleResult(BaseModel):
    status: str = Field(..., description="success, not_found, failed, timeout, unavailable, rate_limited")
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

class AnalyzeResponse(BaseModel):
    target: TargetInfo
    started_at: str
    completed_at: str
    checks: Dict[str, ModuleResult]
