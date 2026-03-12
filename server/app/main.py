from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from server.app.api.agent import router as agent_router
from server.app.api.analytics import router as analytics_router
from server.app.db.base import init_db

app = FastAPI(title="Server Security Monitor")

templates = Jinja2Templates(directory="server/app/templates")

app.mount("/static", StaticFiles(directory="server/app/static"), name="static")


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """
    Main web UI dashboard. Data is loaded on the client side via fetch()
    from the /api/analytics endpoints.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})


app.include_router(agent_router)
app.include_router(analytics_router)