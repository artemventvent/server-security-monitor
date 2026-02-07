from .session import engine, Base
from .models import Host, Report, CheckResult
import asyncio

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
