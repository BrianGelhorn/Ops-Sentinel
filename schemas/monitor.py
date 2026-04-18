from typing import Literal
from pydantic import BaseModel

class HttpMonitorConfig(BaseModel):
    url: str
    expected_status: int = 202


class MonitorCreate(BaseModel):
    title: str
    type: Literal["http"]
    interval_seconds: int
    config: HttpMonitorConfig

class MonitorResponse(MonitorCreate):
    id: int

