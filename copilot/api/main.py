from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from copilot.api.routes import query, health

app = FastAPI(
    title="ReAct Research Copilot",
    description="A single-agent research copilot using the ReAct pattern",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(health.router)
app.include_router(query.router)


@app.get("/")
def root():
    return {"message": "ReAct Research Copilot API", "docs": "/docs"}