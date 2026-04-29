from database.dbmodels import Monitor
from sqlalchemy.orm import Session
from fastapi import Depends
from database.dbconection import get_db
from database.crud import get_all_from_database
from services.check_runner_service import run_monitor_check
import asyncio
from datetime import datetime

taskScheduler: asyncio.Task

async def run_scheduler_loop():
    while True:
        for monitor in should_run():
            asyncio.Task(run_monitor_check(monitor.id))
        await asyncio.sleep(5)

def should_run(db: Session = Depends(get_db)) -> list[Monitor]:
    monitors : list[Monitor] = get_all_from_database(Monitor, db)
    return list(
        filter(
            lambda monitor: monitor.last_checked_at is None or (datetime.now() - monitor.last_checked_at).total_seconds() > monitor.interval_seconds, monitors
            ))

    

def start_scheduler_loop():
    taskScheduler = asyncio.Task(run_scheduler_loop())

def stop_scheduler_loop():
    taskScheduler.get_loop().call_soon_threadsafe(taskScheduler.cancel)
    pass