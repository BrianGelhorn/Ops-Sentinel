from pydantic import BaseModel
from datetime import datetime

class Trigger(BaseModel):
    type: str
    expected_status: int
    observed_status: int
    failed_attempts: int

class Evidence(BaseModel):
    response_time_in_ms: int
    cpu_usage_percent: float
    memory_usage_percent: float
    error_message: str

class Resolution(BaseModel):
    action_taken: str
    action_result: str
    date: str

class CreateItem(BaseModel):
    title: str
    service: str
    type: str
    severity: str
    summary: str
    source: str
    trigger: Trigger
    evidence: Evidence
    resolution: Resolution

class Item(CreateItem):
    id: int
    date: datetime
    status: str