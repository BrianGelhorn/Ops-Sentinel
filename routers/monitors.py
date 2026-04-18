from fastapi.routing import APIRouter
from schemas.monitor import MonitorCreate, MonitorResponse
from services.monitor_service import create_monitor
from database.crud import upload_to_database
import services.check_runner_service
router = APIRouter()

@router.post("/monitor", response_model=MonitorResponse)
async def post_monitor(monitor: MonitorCreate):
    monitordb = create_monitor(monitor)
    upload_to_database(monitordb)
    services.check_runner_service.run_monitor_check(monitordb.id)
    response = MonitorResponse(**monitor.model_dump(), id=monitordb.id)
    return response