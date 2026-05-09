from database.dbmodels import Monitor
from database.dbconection import Session
from database.crud import get_all_from_database
from services.check_runner_service import run_monitor_check
import asyncio
import logging
from datetime import datetime
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Intervalo configurable (en segundos)
SCHEDULER_INTERVAL = int(os.getenv("SCHEDULER_INTERVAL", 5))

taskScheduler: asyncio.Task | None = None
running_tasks: set[asyncio.Task] = set()


async def run_scheduler_loop():
    logger.info("Scheduler loop started")
    while True:
        try:
            monitors = should_run()
            logger.debug(f"Found {len(monitors)} monitors to check")
            for monitor in monitors:
                task = asyncio.create_task(run_monitor_check(monitor.id))
                running_tasks.add(task)
                task.add_done_callback(handle_monitor_task_done)
        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}")
        await asyncio.sleep(SCHEDULER_INTERVAL)


def should_run() -> list[Monitor]:
    db = Session()
    try:
        monitors: list[Monitor] = get_all_from_database(Monitor, db)
        now = datetime.now()
        return list(
            filter(
                lambda monitor: 
                monitor.last_checked_at is None 
                or (
                    (now - monitor.last_checked_at).total_seconds() > monitor.interval_seconds),
                    monitors))
    finally:
        db.close()


def handle_monitor_task_done(task: asyncio.Task):
    running_tasks.discard(task)
    try:
        task.result()
    except asyncio.CancelledError:
        pass
    except Exception:
        logger.exception("Monitor check task failed")

    
def start_scheduler_loop():
    global taskScheduler
    if taskScheduler is None or taskScheduler.done():
        taskScheduler = asyncio.create_task(run_scheduler_loop())
        logger.info("Scheduler loop started")


def stop_scheduler_loop():
    global taskScheduler
    if taskScheduler is not None and not taskScheduler.done():
        taskScheduler.cancel()
        logger.info("Scheduler loop stopped")
    taskScheduler = None
