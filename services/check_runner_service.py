from database.crud import get_from_database, upload_to_database, create_incident
from schemas.incident import IncidentCreate, TriggerCreate, EvidenceCreate, ResolutionCreate
from database.dbmodels import Monitor
from httpx import get, Response, codes, AsyncClient, RequestError
import asyncio
import psutil

async def run_monitor_check(monitorid: int):
    monitor = get_from_database(Monitor, monitorid)
    response: Response
    if monitor is None:
        #TODO: Implement incident creation
        return
    try:
        async with AsyncClient(timeout=5) as client:
            response = await client.get(monitor.config.url)
        if not response.status_code == monitor.config.expected_status:
            #Call to avoid 0% display
            psutil.cpu_percent(None)
            await asyncio.sleep(1)
            incident = create_incident(IncidentCreate(
                title="Error in get", #TODO
                service="test-service", #TODO
                type="http-error", #TODO: Complete
                severity="medium", #TODO
                summary="The provided url didnt respond succesfully", #TODO
                source=f"{monitor.config.url}",
                trigger=TriggerCreate(
                    type="TODO", #TODO
                    expected_status=monitor.config.expected_status,
                    observed_status=response.status_code,
                    failed_attempts=1 #TODO
                ),
                evidence=EvidenceCreate(
                    response_time_in_ms=int(response.elapsed.total_seconds()*1000),
                    cpu_usage_percent=psutil.cpu_percent(None),
                    memory_usage_percent=psutil.virtual_memory().percent,
                    error_message=create_error_message(response, monitor.config.expected_status)
                ),
                resolution=ResolutionCreate(
                    action_result="TODO", #TODO
                    action_taken="TODO", #TODO
                    date="TODO" #TODO
                )
            ))
            upload_to_database(incident)
    except RequestError as e:
        #Call to avoid 0% display
        psutil.cpu_percent(None)
        await asyncio.sleep(1)
        incident = create_incident(IncidentCreate(
            title="Error in get", #TODO
            service="test-service", #TODO
            type="http-error", #TODO: Complete
            severity="medium", #TODO
            summary="The provided url didnt respond succesfully", #TODO
            source=f"{monitor.config.url}",
            trigger=TriggerCreate(
                type="TODO", #TODO
                expected_status=monitor.config.expected_status,
                observed_status=-1, #TODO
                failed_attempts=1 #TODO
            ),
            evidence=EvidenceCreate(
                response_time_in_ms=-1, #TODO
                cpu_usage_percent=psutil.cpu_percent(None),
                memory_usage_percent=psutil.virtual_memory().percent,
                error_message=str(e)
            ),
            resolution=ResolutionCreate(
                action_result="TODO", #TODO
                action_taken="TODO", #TODO
                date="TODO" #TODO
            )
        ))
        upload_to_database(incident)


def create_error_message(response: Response, expected_code: int):
    if response.is_client_error:
        return f"There was an error on the client side. Returned with code: {response.status_code} {response.reason_phrase}"
    elif response.is_server_error:
        return f"There was an error on the server side. Returned with code: {response.status_code} {response.reason_phrase}"
    else:
        return f"The server is alive but the expected code {expected_code} did not match the expected code {response.status_code} {response.reason_phrase}"
    
    