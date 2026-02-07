from server.app.db.session import AsyncSessionLocal
from server.app.db.models import Host, Report, CheckResult
from datetime import datetime
from sqlalchemy import select
from server.app.services.scoring import calculate_report_score

async def ingest_report(data):
    async with AsyncSessionLocal() as session:
        # 1. Host
        result = await session.execute(
            select(Host).where(Host.hostname == data.agent.hostname)
        )
        host = result.scalar_one_or_none()

        if not host:
            host = Host(
                hostname=data.agent.hostname,
                ip=data.agent.ip,
                os=data.agent.os,
                os_version=data.agent.os_version,
            )
            session.add(host)
            await session.flush()  # получить host.id
        else:
            host.last_seen = datetime.utcnow()

        # 2. Report
        report = Report(
            host_id=host.id,
            policy_name=data.policy.name,
            policy_version=data.policy.version,
            timestamp=datetime.fromisoformat(data.timestamp.replace("Z", ""))
        )
        session.add(report)
        await session.flush()

        # 3. Check results
        for r in data.results:
            cr = CheckResult(
                report_id=report.id,
                check_id=r.check_id,
                title=r.title,
                status=r.status,
                severity=r.severity,
                evidence=r.evidence,
                recommendation=r.recommendation
            )
            
            session.add(cr)
        score = await calculate_report_score(report.id)
        print("=== SCORE RESULT ===")
        print(score)
        print("====================")

        await session.commit()
        