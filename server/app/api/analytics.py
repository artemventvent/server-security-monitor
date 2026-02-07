from fastapi import APIRouter
from sqlalchemy import select, func
from server.app.db.session import AsyncSessionLocal
from server.app.db.models import Host, Report, CheckResult
from server.app.services.scoring import calculate_report_score

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/hosts")
async def list_hosts():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Host))
        hosts = result.scalars().all()

        data = []
        for h in hosts:
            data.append({
                "id": h.id,
                "hostname": h.hostname,
                "ip": h.ip,
                "os": h.os,
            })

        return data


@router.get("/hosts/{host_id}")
async def host_details(host_id: int):
    async with AsyncSessionLocal() as session:
        host = await session.get(Host, host_id)
        if not host:
            return {"error": "not found"}

        return {
            "id": host.id,
            "hostname": host.hostname,
            "ip": host.ip,
            "os": host.os,
            "created_at": host.created_at
        }


@router.get("/hosts/{host_id}/score")
async def host_score(host_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Report)
            .where(Report.host_id == host_id)
            .order_by(Report.created_at.desc())
            .limit(1)
        )
        report = result.scalar_one_or_none()
        if not report:
            return {"error": "no reports"}

        score = await calculate_report_score(report.id)
        return score


@router.get("/reports/{report_id}/score")
async def report_score(report_id: int):
    score = await calculate_report_score(report_id)
    return score


@router.get("/dashboard")
async def dashboard():
    async with AsyncSessionLocal() as session:
        hosts_count = await session.scalar(select(func.count(Host.id)))
        reports_count = await session.scalar(select(func.count(Report.id)))

        result = await session.execute(select(CheckResult))
        checks = result.scalars().all()

        total = len(checks)
        fails = len([c for c in checks if c.status == "fail"])
        errors = len([c for c in checks if c.status == "error"])

        return {
            "hosts": hosts_count,
            "reports": reports_count,
            "checks_total": total,
            "fails": fails,
            "errors": errors,
            "security_index": round(100 - ((fails + errors) / max(total,1)) * 100, 2)
        }


@router.get("/top-risks")
async def top_risks(limit: int = 10):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CheckResult.check_id, func.count(CheckResult.id).label("cnt"))
            .where(CheckResult.status == "fail")
            .group_by(CheckResult.check_id)
            .order_by(func.count(CheckResult.id).desc())
            .limit(limit)
        )

        return [
            {"check_id": r[0], "count": r[1]}
            for r in result.all()
        ]
