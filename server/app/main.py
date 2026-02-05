from fastapi import FastAPI
from server.app.api.agent import router as agent_router

app = FastAPI(title="Server Security Monitor")

app.include_router(agent_router)