from database.crud import get_from_database, upload_to_database, create_incident
from schemas.incident import IncidentCreate, TriggerCreate, EvidenceCreate, ResolutionCreate
from database.dbmodels import Monitor
from httpx import get
import asyncio
import psutil

async def run_monitor_check(monitorid: int):
    monitor = get_from_database(Monitor, monitorid)
    if monitor is None:
        #TODO: Implement incident creation
        return
    response = get(monitor.config.url)
    if not response.status_code == monitor.config.expected_status:
        #Call to avoid 0% display
        psutil.cpu_percent(None)
        await asyncio.sleep(1)
        incident = create_incident(IncidentCreate(
            title="Error in get",
            service="test-service",
            type="http-error",
            severity="medium",
            summary="The provided url didnt respond succesfully",
            source=f"{monitor.config.url}",
            trigger=TriggerCreate(
                type="TODO",
                expected_status=monitor.config.expected_status,
                observed_status=response.status_code,
                failed_attempts=1
            ),
            evidence=EvidenceCreate(
                response_time_in_ms=response.elapsed.seconds*1000,
                cpu_usage_percent=psutil.cpu_percent(None),
                memory_usage_percent=psutil.virtual_memory().percent,
                error_message=response.text
            ),
            resolution=ResolutionCreate(
                action_result="TODO",
                action_taken="TODO",
                date="TODO"
            )
        ))
        upload_to_database(incident)