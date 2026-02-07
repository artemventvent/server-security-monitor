from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .session import Base

class Host(Base):
    __tablename__ = "hosts"

    id = Column(Integer, primary_key=True)
    hostname = Column(String, unique=True)
    ip = Column(String)
    os = Column(String)
    os_version = Column(String)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)

    reports = relationship("Report", back_populates="host")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey("hosts.id"))
    policy_name = Column(String)
    policy_version = Column(String)
    timestamp = Column(DateTime)

    host = relationship("Host", back_populates="reports")
    results = relationship("CheckResult", back_populates="report")


class CheckResult(Base):
    __tablename__ = "check_results"

    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey("reports.id"))
    check_id = Column(String)
    title = Column(String)
    status = Column(String)
    severity = Column(String)
    evidence = Column(Text)
    recommendation = Column(Text)

    report = relationship("Report", back_populates="results")
