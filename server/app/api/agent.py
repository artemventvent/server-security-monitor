from fastapi import APIRouter
from server.app.schemas import AgentReport

router = APIRouter(prefix="/api/agent")

@router.post("/report")
async def report(data: AgentReport):
    print("=== AGENT REPORT RECEIVED ===")
    print(data.model_dump())
    print("============================")
    return {"status": "ok"}