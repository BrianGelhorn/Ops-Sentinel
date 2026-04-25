from database.crud import get_from_database, upload_to_database, create_incident, get_incidents_from_database
from schemas.incident import IncidentCreate, TriggerCreate, EvidenceCreate, ResolutionCreate
from database.dbmodels import Monitor, Incident
from httpx import get, Response, codes, AsyncClient, RequestError
import asyncio
import psutil

async def run_monitor_check(monitorid: int):
    #Call to avoid 0% display
    psutil.cpu_percent(None)
    await asyncio.sleep(1)
    monitor = get_from_database(Monitor, monitorid)
    response: Response = None
    other_incidents = get_incidents_from_database(monitor_id=monitorid)

    if monitor is None:
        #TODO: Implement incident creation
        return
    try:
        async with AsyncClient(timeout=5) as client:
            response = await client.get(monitor.config.url)

    except RequestError as e:
        incident: Incident = next((inc for inc in other_incidents 
                if inc.monitor_id == monitor.id
                and inc.trigger.observed_status is None), None)
        if incident is None:
            incident = create_incident(IncidentCreate(
                monitor_id=monitorid,
                title="Error in get", #TODO
                service="test-service", #TODO
                type="http-error", #TODO: Complete
                severity="medium", #TODO
                summary="The provided url didnt respond succesfully", #TODO
                source=f"{monitor.config.url}",
                trigger=TriggerCreate(
                    type="TODO", #TODO
                    expected_status=monitor.config.expected_status,
                    observed_status=None if response is None else response.status_code,
                    failed_attempts=1 #TODO
                ),
                evidence=EvidenceCreate(
                    response_time_in_ms=None if response is None else int(response.elapsed.total_seconds()*1000), #TODO
                    last_cpu_usage_percent=psutil.cpu_percent(None),
                    last_memory_usage_percent=psutil.virtual_memory().percent,
                    error_message=str(e)
                ),
                resolution=ResolutionCreate(
                    action_result="TODO", #TODO
                    action_taken="TODO", #TODO
                    date="TODO" #TODO
                )
            ))
        else:
            incident.trigger.failed_attempts += 1
            incident.evidence.last_cpu_usage_percent = psutil.cpu_percent(None)
            incident.evidence.last_memory_usage_percent = psutil.virtual_memory().percent
        upload_to_database(incident)
        return 
    incident: Incident = next((inc for inc in other_incidents 
                    if inc.monitor_id == monitor.id
                    and inc.trigger.observed_status == response.status_code), None)
    if incident is None:
        incident = create_incident(IncidentCreate(
            monitor_id=monitorid,
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
                response_time_in_ms=int(response.elapsed.total_seconds()*1000), #TODO
                last_cpu_usage_percent=psutil.cpu_percent(None),
                last_memory_usage_percent=psutil.virtual_memory().percent,
                error_message=create_error_message(response, monitor.config.expected_status)
            ),
            resolution=ResolutionCreate(
                action_result="TODO", #TODO
                action_taken="TODO", #TODO
                date="TODO" #TODO
            )
        ))
    else:
        incident.trigger.failed_attempts += 1
        incident.evidence.last_cpu_usage_percent = psutil.cpu_percent(None)
        incident.evidence.last_memory_usage_percent = psutil.virtual_memory().percent
    if monitor.config.expected_status != response.status_code:
        upload_to_database(incident)

def create_error_message(response: Response | None, expected_code: int):
    if response.is_client_error:
        return f"There was an error on the client side. Returned with code: {response.status_code} {response.reason_phrase}"
    elif response.is_server_error:
        return f"There was an error on the server side. Returned with code: {response.status_code} {response.reason_phrase}"
    else:
        return f"The server is alive but the expected code {expected_code} did not match the expected code {response.status_code} {response.reason_phrase}"
    
    