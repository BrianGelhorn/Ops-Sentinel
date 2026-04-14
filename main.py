from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/health")
async def get_health():
    return {"status": "alive"}

@app.get("/ready")
async def get_ready():
    #TODO: Give funcionality to the ready depending the status of the api
    return {"status": "ready"}

INCIDENTS=[{"id": 1}, {"id": 2}]

@app.get("/incidents")
async def get_incidents():
    #TODO: Implement the SQLConnection
    return INCIDENTS

class Trigger():
    type: str
    expected_status: int
    observed_status: int
    failed_attempts: int

class Evidence():
    response_time_in_ms: int
    cpu_usage_percent: float
    memory_usage_percent: float
    error_message: str

class Resolution():
    action_taken: str
    action_result: str
    date: str

class Item(BaseModel):
    id: int
    title: str
    service: str
    type: str
    severity: str
    summary: str
    date: str
    source: str
    trigger: Trigger
    evidence: Evidence
    resolution: Resolution



@app.post("/incidents/")
async def post_incidents(item: Item):
    INCIDENTS.append({"id": item.id})
    return item