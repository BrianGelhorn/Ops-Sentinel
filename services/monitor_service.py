from schemas.monitor import MonitorCreate
from crud import upload_to_database
from dbmodels import Monitor, HttpMonitorConfig

def create_monitor(monitor: MonitorCreate):
    monitorData = monitor.model_dump()
    configData = monitor.config.model_dump()

    monitordb = Monitor(**monitorData, 
                        config=HttpMonitorConfig(**configData))
    return monitordb