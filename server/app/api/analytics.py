from fastapi import APIRouter
from sqlalchemy import select, func

from server.app.db.models import CheckResult, Host, Report
from server.app.db.session import AsyncSessionLocal
from server.app.services.scoring import calculate_report_score

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/hosts")
async def list_hosts():
    """
    Lightweight list of all known hosts for the web UI.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Host))
        hosts = result.scalars().all()

        return [
            {
                "id": h.id,
                "hostname": h.hostname,
                "ip": h.ip,
                "os": h.os,
                "created_at": h.first_seen,
            }
            for h in hosts
        ]


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
            "created_at": host.first_seen,
            "last_seen": host.last_seen,
        }


@router.get("/hosts/{host_id}/score")
async def host_score(host_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Report)
            .where(Report.host_id == host_id)
            .order_by(Report.timestamp.desc())
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
    """
    High‑level snapshot used on the main dashboard.
    """
    async with AsyncSessionLocal() as session:
        hosts_count = await session.scalar(select(func.count(Host.id)))
        reports_count = await session.scalar(select(func.count(Report.id)))

        result = await session.execute(select(CheckResult))
        checks = result.scalars().all()

        total = len(checks)
        fails = len([c for c in checks if c.status == "fail"])
        errors = len([c for c in checks if c.status == "error"])

        return {
            "hosts": hosts_count or 0,
            "reports": reports_count or 0,
            "checks_total": total,
            "fails": fails,
            "errors": errors,
            "security_index": round(
                100 - ((fails + errors) / max(total, 1)) * 100, 2
            ),
        }


@router.get("/top-risks")
async def top_risks(limit: int = 10):
    """
    Aggregation of failed checks by check id for the "Top risks" chart.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CheckResult.check_id, func.count(CheckResult.id).label("cnt"))
            .where(CheckResult.status == "fail")
            .group_by(CheckResult.check_id)
            .order_by(func.count(CheckResult.id).desc())
            .limit(limit)
        )

        return [
            {"check_id": row[0], "count": row[1]}
            for row in result.all()
        ]


@router.get("/latest-checks")
async def latest_checks(limit: int = 25):
    """
    Latest individual check results with host context for the table.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CheckResult, Report, Host)
            .join(Report, CheckResult.report_id == Report.id)
            .join(Host, Report.host_id == Host.id)
            .order_by(Report.timestamp.desc())
            .limit(limit)
        )

        items = []
        for check, report, host in result.all():
            items.append(
                {
                    "id": check.id,
                    "check_id": check.check_id,
                    "title": check.title,
                    "status": check.status,
                    "severity": check.severity,
                    "hostname": host.hostname,
                    "timestamp": report.timestamp.isoformat() if report.timestamp else None,
                }
            )

        return items
