from fastapi import APIRouter, status
from typing import Optional
from schemas import *
from crud import create_incident, upload_to_database, get_all_from_database, get_incidents_from_database
from dbmodels import Incident
import logging


router = APIRouter(prefix="/incidents")
logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.INFO)

@router.get("", response_model=list[IncidentResponse])
async def get_all_incidents(                      
                    id: Optional[int] = None,
                    title: Optional[str] = None,
                    service: Optional[str] = None,
                    type: Optional[str] = None, 
                    severity: Optional[str] = None,
                    source: Optional[str] = None):
    
    allIncidents = get_incidents_from_database( id=id,
                                                title=title,
                                                service=service,
                                                type=type,
                                                severity=severity,
                                                source=source)
    return allIncidents

@router.get("/{id}", response_model=list[IncidentResponse])
async def get_incidents(id: int=None):
    allIncidents = get_all_from_database(Incident)
    incidents = list(filter(lambda incident: incident.id == id, allIncidents))
    return incidents

@router.post("/", response_model=IncidentCreate, status_code=status.HTTP_201_CREATED)
async def post_incidents(item: IncidentCreate):
    incident = create_incident(item)
    upload_to_database(incident)
    return item