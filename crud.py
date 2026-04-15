from dbconection import session
from dbmodels import Incident, Trigger, Evidence, Resolution
from schemas import CreateItem

def create_incident(item: CreateItem) -> Incident:
    itemData = item.model_dump(exclude={"trigger", "evidence", "resolution"})

    triggerData = item.trigger.model_dump()
    evidenceData = item.evidence.model_dump()
    resolutionData = item.resolution.model_dump()

    incident = Incident(**itemData, 
                        trigger=Trigger(**triggerData), 
                        evidence=Evidence(**evidenceData), 
                        resolution=Resolution(**resolutionData))
    
    return incident

def upload_to_database(item):
    session.add(item)
    session.commit()
    session.refresh(item)