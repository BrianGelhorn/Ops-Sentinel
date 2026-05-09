from database.crud import (get_from_database, 
                           upload_to_database, 
                           create_incident, 
                           get_incidents_from_database)
from sqlalchemy.orm import Session as OrmSession
from database.dbconection import Session as SessionLocal
from sqlalchemy.exc import UnboundExecutionError
from schemas.incident import (IncidentCreate, 
                              TriggerCreate, 
                              EvidenceCreate, 
                              ResolutionCreate)
from database.dbmodels import Monitor, Incident
from httpx import (Response,
                   AsyncClient,
                   RequestError,
                   TimeoutException,
                   ConnectError,
                   NetworkError,
                   ProtocolError,
                   TooManyRedirects)
import asyncio
import psutil


REQUEST_ERROR_SEVERITY = {
    "timeout-error": "high",
    "connection-error": "high",
    "network-error": "high",
    "protocol-error": "medium",
    "redirect-error": "low",
    "request-error": "medium",
    "client-error": "medium",
    "server-error": "high",
    "unexpected-status-error": "medium",
}


async def run_monitor_check(monitorid: int, db: OrmSession | None = None):
    incident: Incident | None = None
    db, owns_db = ensure_bound_session(db)
    try:
        # Call to avoid 0% display
        psutil.cpu_percent(None)
        await asyncio.sleep(1)
        monitor = get_from_database(Monitor, monitorid, db)
        response: Response | None = None
        incidents = get_incidents_from_database(monitor_id=monitorid, db=db)
        
        if monitor is None:
            incident_type = "monitor-not-found"
            source = f"monitor: {monitorid}"
            incident: Incident | None = next(
                (
                    inc
                    for inc in get_incidents_from_database(
                        source=source,
                        type=incident_type,
                        db=db,
                    )
                ),
                None,
            )
            if incident is None:
                incident = create_incident(IncidentCreate(
                    monitor_id=None,
                    title="Monitor check failed",
                    service=source,
                    type=incident_type,
                    severity="high",
                    summary=f"Monitor {monitorid} could not be found for a scheduled check",
                    source=source,
                    trigger=TriggerCreate(
                        type="monitor-lookup",
                        expected_status=0,
                        observed_status=None,
                        failed_attempts=1
                    ),
                    evidence=EvidenceCreate(
                        response_time_in_ms=None,
                        last_cpu_usage_percent=psutil.cpu_percent(None),
                        last_memory_usage_percent=psutil.virtual_memory().percent,
                        error_message=f"Monitor with id {monitorid} was not found"
                    ),
                    resolution=ResolutionCreate(
                        action_result="pending",
                        action_taken="none",
                        date="pending"
                    )
                ))
            else:
                incident.trigger.failed_attempts += 1
                incident.evidence.last_cpu_usage_percent = psutil.cpu_percent(None)
                incident.evidence.last_memory_usage_percent = psutil.virtual_memory().percent
            return
        request_error: RequestError | None = None
        try:
            async with AsyncClient(timeout=5) as client:
                response = await client.get(monitor.config.url)

        except RequestError as e:
            request_error = e
        incident_type: str = "Unknown"
        if request_error is not None:
            incident_type = classify_request_error(request_error)
        if response is not None:
            incident_type = classify_response_error(
                response=response,
                expected_code=monitor.config.expected_status
            )
        if incident_type == "none":
            upload_to_database(monitor, db)
            return

        incident: Incident | None = next(
            (
                inc 
                for inc in incidents 
                if inc.monitor_id == monitor.id 
                and inc.type == incident_type
            ), 
            None,
        )
        if incident is None:
            incident = create_incident(IncidentCreate(
                monitor_id=monitorid,
                title=f"{monitor.type.title()} check failed",
                service=monitor.title,
                type=incident_type,
                severity=REQUEST_ERROR_SEVERITY[incident_type],
                summary=create_incident_summary(
                    incident_type=incident_type,
                    url=monitor.config.url,
                    expected_code=monitor.config.expected_status,
                    observed_code=None if response is None else response.status_code,
                ),
                source=f"{monitor.config.url}",
                trigger=TriggerCreate(
                    type="http-request" if request_error is not None else "http-status",
                    expected_status=monitor.config.expected_status,
                    observed_status=None if response is None else response.status_code,
                    failed_attempts=1
                ),
                evidence=EvidenceCreate(
                    response_time_in_ms=(int(response.elapsed.total_seconds() * 1000)
                                         if response is not None 
                                         else None),
                    last_cpu_usage_percent=psutil.cpu_percent(None),
                    last_memory_usage_percent=psutil.virtual_memory().percent,
                    error_message=create_error_message(response, monitor.config.expected_status)
                ),
                resolution=ResolutionCreate(
                    action_result="pending",
                    action_taken="none",
                    date="pending"
                )
            ))
        else:
            incident.trigger.failed_attempts += 1
            incident.evidence.last_cpu_usage_percent = psutil.cpu_percent(None)
            incident.evidence.last_memory_usage_percent = psutil.virtual_memory().percent
    finally:
        if incident is not None:
            upload_to_database(incident, db)
        if owns_db:
            db.close()


def ensure_bound_session(db: OrmSession | None) -> tuple[OrmSession, bool]:
    if db is None or isinstance(db, type):
        return SessionLocal(), True
    try:
        db.get_bind()
    except UnboundExecutionError:
        db.close()
        return SessionLocal(), True
    return db, False


def create_error_message(response: Response | None, expected_code: int):
    if response is not None:
        if response.is_client_error:
            return (f"There was an error on the client side. "
                    f"Returned with code: {response.status_code} {response.reason_phrase}")
        elif response.is_server_error:
            return (f"There was an error on the server side. "
                    f"Returned with code: {response.status_code} {response.reason_phrase}")
        else:
            return (f"The server is alive but the expected code {expected_code} "
                    f"did not match the expected code {response.status_code} "
                    f"{response.reason_phrase}")
    return "Uknown Error"


def create_incident_summary(
        incident_type: str,
        url: str,
        expected_code: int,
        observed_code: int | None) -> str:
    if observed_code is None:
        return f"{url} failed during the HTTP request with {incident_type.replace('-', ' ')}"
    return (f"{url} returned HTTP {observed_code}; "
            f"expected HTTP {expected_code}")


def classify_request_error(error: RequestError) -> str:
    if isinstance(error, TimeoutException):
        return "timeout-error"
    if isinstance(error, ConnectError):
        return "connection-error"
    if isinstance(error, NetworkError):
        return "network-error"
    if isinstance(error, ProtocolError):
        return "protocol-error"
    if isinstance(error, TooManyRedirects):
        return "redirect-error"
    return "request-error"


def classify_response_error(response: Response, expected_code: int) -> str:
    if response.status_code == expected_code:
        return "none"
    if response.is_client_error:
        return "client-error"
    if response.is_server_error:
        return "server-error"
    if response.is_redirect:
        return "redirect-error"
    return "unexpected-status-error"
    
    
