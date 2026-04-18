from dbconection import DBaseModel
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

class Incident(DBaseModel):
    __tablename__ = "incident"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)
    title = Column(String, nullable=False)
    service = Column(String, nullable=False)
    type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    source = Column(String, nullable=False)

    trigger = relationship("Trigger", back_populates="incident", uselist=False)
    evidence = relationship("Evidence", back_populates="incident", uselist=False)
    resolution = relationship("Resolution", back_populates="incident", uselist=False)


class Trigger(DBaseModel):
    __tablename__ = "trigger"

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    expected_status = Column(Integer, nullable=False)
    observed_status = Column(Integer, nullable=False)
    failed_attempts = Column(Integer, nullable=False)
    incident_id = Column(Integer, ForeignKey("incident.id"), unique=True)

    incident = relationship("Incident", back_populates="trigger")

class Evidence(DBaseModel):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True)
    response_time_in_ms = Column(Integer, nullable=False)
    cpu_usage_percent = Column(Float, nullable=False)
    memory_usage_percent = Column(Float, nullable=False)
    error_message = Column(String, nullable=False)
    incident_id = Column(Integer, ForeignKey("incident.id"), unique=True)

    incident = relationship("Incident", back_populates="evidence")

class Resolution(DBaseModel):
    __tablename__ = "resolution"

    id = Column(Integer, primary_key=True)
    action_taken = Column(String, nullable=False)
    action_result = Column(String, nullable=False)
    date = Column(String, nullable=False)
    incident_id = Column(Integer, ForeignKey("incident.id"), unique=True)

    incident = relationship("Incident", back_populates="resolution")

class Monitor(DBaseModel):
    __tablename__ = "monitor"

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    interval = Column(Integer, nullable=False)
    
    config = relationship("HttpMonitorConfig", back_populates="monitor")

class HttpMonitorConfig(DBaseModel):
    __tablename__ = "httpmonitorconfig"
    id = Column(Integer, primary_key=True)
    host = Column(String, nullable=False)
    expected_status = Column(Integer, nullable=False)
    monitor_id = Column(Integer, ForeignKey("monitor.id"), unique=True)

    monitor = relationship("Monitor", back_populates="httpmonitorconfig")