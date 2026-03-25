from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class StepLog(BaseModel):
    step: int
    action: str
    args: dict
    observation: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    steps: list[StepLog]
    step_count: int


class HealthResponse(BaseModel):
    status: str
    message: str