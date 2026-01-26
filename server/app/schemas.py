from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime


Severity = Literal["low", "medium", "high"]
Status = Literal["pass", "fail"]


class Finding(BaseModel):
    source: str = Field(..., example="lynis")
    check_id: str = Field(..., example="SSH_ROOT_LOGIN")
    severity: Severity
    status: Status
    description: str
    remediation: str


class AgentReport(BaseModel):
    agent_id: str
    hostname: str
    os: str
    timestamp: datetime
    findings: List[Finding]