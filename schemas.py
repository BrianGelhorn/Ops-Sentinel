from pydantic import BaseModel, ConfigDict
from datetime import datetime

class TriggerCreate(BaseModel):
    type: str
    expected_status: int
    observed_status: int
    failed_attempts: int

class EvidenceCreate(BaseModel):
    response_time_in_ms: int
    cpu_usage_percent: float
    memory_usage_percent: float
    error_message: str

class ResolutionCreate(BaseModel):
    action_taken: str
    action_result: str
    date: str

class IncidentCreate(BaseModel):
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
    status: str