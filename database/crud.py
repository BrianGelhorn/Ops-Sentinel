from database.dbconection import session
from database.dbmodels import Incident, Trigger, Evidence, Resolution
from schemas.incident import *
from datetime import datetime, UTC
from typing import Optional

def create_incident(item: IncidentCreate) -> Incident:
    itemData = item.model_dump(exclude={"trigger", "evidence", "resolution"})

    triggerData = item.trigger.model_dump()
    evidenceData = item.evidence.model_dump()
    resolutionData = item.resolution.model_dump()

    incident = Incident(**itemData, 
                        trigger=Trigger(**triggerData), 
                        evidence=Evidence(**evidenceData), 
                        resolution=Resolution(**resolutionData),
                        date=datetime.now(UTC),
                        status="Uknown")
    
    return incident

def upload_to_database(item):
    session.add(item)
    session.commit()
    session.refresh(item)

def get_from_database(model, id):
    return session.get(model, id)



def get_all_from_database(model):
    return session.query(model).all()

def get_incidents_from_database(                      
                    id: Optional[int] = None,
                    monitor_id: Optional[int] = None,
                    title: Optional[str] = None,
                    service: Optional[str] = None,
                    type: Optional[str] = None, 
                    severity: Optional[str] = None,
                    source: Optional[str] = None):
    query = session.query(Incident)

    if id is not None:
        query = query.filter(Incident.id == id)
    
    if monitor_id is not None:
        query = query.filter(Incident.monitor_id == monitor_id)

    if title is not None:
        query = query.filter(Incident.title == title)
    
    if service is not None:
        query = query.filter(Incident.service == service)

    if type is not None:
        query = query.filter(Incident.type == type)
    
    if severity is not None:
        query = query.filter(Incident.severity == severity)

    if source is not None:
        query = query.filter(Incident.source == source)
    return query.all()

    