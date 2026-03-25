from fastapi import APIRouter, HTTPException
from copilot.api.schemas import QueryRequest, QueryResponse
from copilot.agent.react_agent import run_react_agent

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    result = run_react_agent(request.question)
    return QueryResponse(**result)