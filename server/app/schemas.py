from pydantic import BaseModel
from typing import List, Optional

class AgentInfo(BaseModel):
    id: str
    hostname: str
    ip: str
    os: str
    os_version: str

class PolicyInfo(BaseModel):
    name: str
    version: str

class CheckResult(BaseModel):
    check_id: str
    title: str
    status: str
    severity: str
    evidence: Optional[str]
    recommendation: Optional[str] = None

class AgentReport(BaseModel):
    agent: AgentInfo
    policy: PolicyInfo
    timestamp: str
    results: List[CheckResult]