from typing import Literal
from pydantic import BaseModel, ConfigDict


class HttpMonitorConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: str
    expected_status: int = 202


class MonitorCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    type: Literal["http"]
    interval_seconds: int
    config: HttpMonitorConfig


class MonitorResponse(MonitorCreate):
    id: int
