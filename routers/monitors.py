from fastapi.routing import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from schemas.monitor import MonitorCreate, MonitorResponse
from services.monitor_service import create_monitor
from database.crud import upload_to_database, get_all_from_database
from database.dbmodels import Incident, Monitor
from database.dbconection import get_db
from schemas.incident import IncidentResponse
router = APIRouter(prefix="/monitor")


@router.post("/", response_model=MonitorResponse)
async def post_monitor(monitor: MonitorCreate, db: Session = Depends(get_db)):
    monitordb = create_monitor(monitor)
    upload_to_database(monitordb, db)
    response = MonitorResponse(**monitor.model_dump(), id=monitordb.id)
    return response


@router.get("/", response_model=list[MonitorResponse])
async def get_all_monitors(db: Session = Depends(get_db)):
    monitors = get_all_from_database(Monitor, db)
    return monitors


@router.get("/get_active_incidents", response_model=list[IncidentResponse])
async def get_active_incidents_for_monitor(monitorid: int, db: Session = Depends(get_db)):
    return (
        db.query(Incident)
        .filter(Incident.monitor_id == monitorid, Incident.status != "resolved")
        .all()
    )
