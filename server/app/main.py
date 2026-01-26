from fastapi import FastAPI
from app.schemas import AgentReport

app = FastAPI(
    title="Server Security Monitor",
    version="0.1.0"
)


@app.get("/health")
def healthcheck():
    return {"status": "ok"}


@app.post("/api/agent/report")
def receive_report(report: AgentReport):
    # Пока просто логируем
    print("Report received from:", report.hostname)
    print("Findings:", len(report.findings))
    return {"status": "accepted"}