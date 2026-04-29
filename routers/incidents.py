from fastapi import APIRouter, status, HTTPException, Depends
from typing import Optional
from schemas.incident import *
from database.dbconection import get_db
from database.crud import (
    create_incident, 
    upload_to_database, 
    get_all_from_database, 
    get_incidents_from_database, 
    get_from_database)
from database.dbmodels import Incident
from sqlalchemy.orm import Session
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
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    allIncidents = get_incidents_from_database(id=id,
                                               title=title,
                                               service=service,
                                               type=type,
                                               severity=severity,
                                               source=source,
                                               db=db)
    return allIncidents


@router.get("/{id}", response_model=list[IncidentResponse])
async def get_incidents(
    id: int | None = None, 
    db: Session = Depends(get_db)
):
    allIncidents = get_all_from_database(Incident, db)
    incidents = list(
        filter(lambda incident: 
               incident.id == id, 
               allIncidents))
    return incidents


@router.post("/", 
             response_model=IncidentCreate, 
             status_code=status.HTTP_201_CREATED)
async def post_incidents(item: IncidentCreate, db: Session = Depends(get_db)):
    incident = create_incident(item)
    upload_to_database(incident, db)
    return item


@router.patch("/{id}")
async def patch_incidents(
    id: int, 
    incidentPatch: IncidentPatch, 
    db: Session = Depends(get_db)
):
    incident: Incident = get_from_database(Incident, id, db)  
    
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident Not Found")
    
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
    
    upload_to_database(incident, db) 