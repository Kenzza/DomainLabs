from fastapi import APIRouter, HTTPException, status
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from app.services.analyzer_service import run_analysis
from app.core.security import normalize_and_validate_target, SecurityError

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_target(request: AnalyzeRequest):
    try:
        validated_target = normalize_and_validate_target(request.target)
    except SecurityError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validasi target gagal: {str(e)}"
        )
    
    result = run_analysis(request, validated_target)
    return result
