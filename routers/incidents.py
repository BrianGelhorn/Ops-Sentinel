from fastapi import APIRouter, status
from pydantic import BaseModel
from datetime import datetime
router = APIRouter(prefix="/incidents")


#TODO: Implement the SQLConnection
INCIDENTS=[]

@router.get("")
async def get_incidents():
    return INCIDENTS

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



@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def post_incidents(itemToAdd: CreateItem):
    item = Item(
        id=1,
        title=itemToAdd.title,
        service=itemToAdd.service,
        type=itemToAdd.type,
        severity=itemToAdd.severity,
        summary=itemToAdd.summary,
        source=itemToAdd.source,
        trigger=itemToAdd.trigger,
        evidence=itemToAdd.evidence,
        resolution=itemToAdd.resolution,
        date=datetime.now(),
        status="open"
    )
    INCIDENTS.append(item)
    return item