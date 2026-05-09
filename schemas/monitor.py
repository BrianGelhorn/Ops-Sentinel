from typing import Literal
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator


class HttpMonitorConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: str
    expected_status: int = Field(default=202, ge=100, le=599)

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        return str(AnyHttpUrl(value))


class MonitorCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    type: Literal["http"]
    interval_seconds: int = Field(gt=0)
    config: HttpMonitorConfig


class MonitorResponse(MonitorCreate):
    id: int
