from database.dbconection import DBaseModel
from sqlalchemy import Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

class Incident(DBaseModel):
    __tablename__ = "incident"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    service: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    summary: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)

    trigger: Mapped["Trigger"] = relationship("Trigger", back_populates="incident", uselist=False)
    evidence: Mapped["Evidence"] = relationship("Evidence", back_populates="incident", uselist=False)
    resolution: Mapped["Resolution"] = relationship("Resolution", back_populates="incident", uselist=False)


class Trigger(DBaseModel):
    __tablename__ = "trigger"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    expected_status: Mapped[int] = mapped_column(Integer, nullable=False)
    observed_status: Mapped[int] = mapped_column(Integer, nullable=False)
    failed_attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    incident_id: Mapped[int] = mapped_column(Integer, ForeignKey("incident.id"), unique=True)

    incident: Mapped["Incident"] = relationship("Incident", back_populates="trigger")

class Evidence(DBaseModel):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    response_time_in_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    cpu_usage_percent: Mapped[float] = mapped_column(Float, nullable=False)
    memory_usage_percent: Mapped[float] = mapped_column(Float, nullable=False)
    error_message: Mapped[str] = mapped_column(String, nullable=False)
    incident_id: Mapped[int] = mapped_column(Integer, ForeignKey("incident.id"), unique=True)

    incident: Mapped["Incident"] = relationship("Incident", back_populates="evidence")

class Resolution(DBaseModel):
    __tablename__ = "resolution"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action_taken: Mapped[str] = mapped_column(String, nullable=False)
    action_result: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[str] = mapped_column(String, nullable=False)
    incident_id: Mapped[int] = mapped_column(Integer, ForeignKey("incident.id"), unique=True)

    incident: Mapped["Incident"] = relationship("Incident", back_populates="resolution")

class HttpMonitorConfig(DBaseModel):
    __tablename__ = "httpmonitorconfig"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    expected_status: Mapped[int] = mapped_column(Integer, nullable=False)
    monitor_id: Mapped[int] = mapped_column(Integer, ForeignKey("monitor.id"), unique=True)

    monitor: Mapped["Monitor"] = relationship("Monitor", back_populates="config")

class Monitor(DBaseModel):
    __tablename__ = "monitor"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    interval: Mapped[int] = mapped_column(Integer, nullable=False)
    
    config: Mapped["HttpMonitorConfig"] = relationship("HttpMonitorConfig", back_populates="monitor")