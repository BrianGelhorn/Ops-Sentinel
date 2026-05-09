from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Literal


IncidentStatus = Literal["open", "acknowledged", "resolved"]


class TriggerCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str
    expected_status: int
    observed_status: int | None
    failed_attempts: int


class EvidenceCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    response_time_in_ms: int | None
    last_cpu_usage_percent: float
    last_memory_usage_percent: float
    error_message: str


class ResolutionCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    action_taken: str | None = None
    action_result: str | None = None
    date: str | None = None


class IncidentCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    monitor_id: int | None
    title: str
    service: str
    type: str
    severity: str
    summary: str
    source: str
    trigger: TriggerCreate
    evidence: EvidenceCreate
    resolution: ResolutionCreate


class TriggerResponse(TriggerCreate):
    id: int
    incident_id: int


class EvidenceResponse(EvidenceCreate):
    id: int
    incident_id: int


class ResolutionResponse(ResolutionCreate):
    id: int
    incident_id: int


class IncidentResponse(IncidentCreate):
    id: int
    date: datetime
    status: IncidentStatus


class IncidentPatch(BaseModel):
    status: IncidentStatus | None = None
    summary: str | None = None
    severity: str | None = None
    resolution: ResolutionCreate | None = None
