from dbconection import session
from dbmodels import Incident, Trigger, Evidence, Resolution
from schemas import *
from datetime import datetime, UTC

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