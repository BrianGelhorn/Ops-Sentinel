from fastapi.routing import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from schemas.monitor import MonitorCreate, MonitorResponse
from services.monitor_service import create_monitor
from database.crud import upload_to_database, get_all_from_database
from database.dbmodels import Monitor
from database.dbconection import get_db
router = APIRouter()


@router.post("/monitor", response_model=MonitorResponse)
async def post_monitor(monitor: MonitorCreate, db: Session = Depends(get_db)):
    monitordb = create_monitor(monitor)
    upload_to_database(monitordb, db)
    response = MonitorResponse(**monitor.model_dump(), id=monitordb.id)
    return response


@router.get("/monitor", response_model=list[MonitorResponse])
async def get_all_monitors(db: Session = Depends(get_db)):
    monitors = get_all_from_database(Monitor, db)
    return monitors