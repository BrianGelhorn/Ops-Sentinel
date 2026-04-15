from fastapi import APIRouter, status
from schemas import *
from crud import create_incident, upload_to_database, get_all_from_database
from dbmodels import Incident

router = APIRouter(prefix="/incidents")

@router.get("", response_model=list[IncidentResponse])
async def get_incidents():
    return get_all_from_database(Incident)

@router.post("/", response_model=IncidentCreate, status_code=status.HTTP_201_CREATED)
async def post_incidents(item: IncidentCreate):
    incident = create_incident(item)
    upload_to_database(incident)
    return item