from fastapi import APIRouter
from server.app.schemas import AgentReport
from server.app.services.ingest import ingest_report

router = APIRouter(prefix="/api/agent")

@router.post("/report")
async def report(data: AgentReport):
    await ingest_report(data)
    return {"status": "ok"}