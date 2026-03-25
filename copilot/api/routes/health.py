from fastapi import APIRouter
from copilot.api.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="ok",
        message="ReAct Research Copilot is running"
    )