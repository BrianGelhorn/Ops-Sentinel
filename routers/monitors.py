from fastapi.routing import APIRouter
from schemas.monitor import *

router = APIRouter("/")

@router.post("monitor", response_model=MonitorResponse)
async def post_monitor(monitor: MonitorCreate):
    