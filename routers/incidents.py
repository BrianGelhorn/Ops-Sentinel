from fastapi import APIRouter, status
from typing import Optional
from schemas import *
from crud import create_incident, upload_to_database, get_all_from_database, get_incidents_from_database, get_from_database
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

@router.patch("/{id}")
async def patch_incidents(id: int = None, incidentPatch: IncidentPatch = None):
    incident: Incident = get_from_database(Incident, id)  
    if incidentPatch.status is not None:
        incident.status = incidentPatch.status
    if incidentPatch.summary is not None:
        incident.summary = incidentPatch.summary
    if incidentPatch.severity is not None:
        incident.severity = incidentPatch.severity
    if incidentPatch.resolution is not None:
        if incidentPatch.resolution.action_taken is not None:
            incident.resolution.action_taken = incidentPatch.resolution.action_taken
        if incidentPatch.resolution.date is not None:
            incident.resolution.date = incidentPatch.resolution.date
        if incidentPatch.resolution.action_result is not None:
            incident.resolution.action_result = incidentPatch.resolution.action_result
    
    upload_to_database(incident)