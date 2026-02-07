from fastapi import FastAPI
from server.app.api.agent import router as agent_router
from server.app.db.base import init_db
from server.app.api.analytics import router as analytics_router

app = FastAPI(title="Server Security Monitor")

@app.on_event("startup")
async def startup():
    await init_db()

app.include_router(agent_router)
app.include_router(analytics_router)