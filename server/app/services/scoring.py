from sqlalchemy import select
from server.app.db.models import Host, Report, CheckResult
from server.app.db.session import AsyncSessionLocal

SEVERITY_WEIGHTS = {
    "low": 1,
    "medium": 3,
    "high": 7,
    "critical": 10
}

STATUS_MULTIPLIER = {
    "pass": 0,
    "fail": 1,
    "error": 0.5,
    "warn": 0.3
}

async def calculate_report_score(report_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CheckResult).where(CheckResult.report_id == report_id)
        )
        checks = result.scalars().all()

        total_risk = 0
        max_risk = 0

        detailed = []

        for c in checks:
            weight = SEVERITY_WEIGHTS.get(c.severity, 1)
            mult = STATUS_MULTIPLIER.get(c.status, 1)

            risk = weight * mult
            total_risk += risk
            max_risk += weight

            detailed.append({
                "check_id": c.check_id,
                "title": c.title,
                "severity": c.severity,
                "status": c.status,
                "risk": risk
            })

        score = 0
        if max_risk > 0:
            score = round((total_risk / max_risk) * 100, 2)

        level = classify_score(score)

        return {
            "report_id": report_id,
            "risk_score": score,   # 0–100
            "risk_level": level,   # LOW / MEDIUM / HIGH / CRITICAL
            "details": detailed
        }


def classify_score(score: float) -> str:
    if score < 15:
        return "LOW"
    elif score < 40:
        return "MEDIUM"
    elif score < 70:
        return "HIGH"
    else:
        return "CRITICAL"
