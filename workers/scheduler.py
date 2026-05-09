from database.dbmodels import Monitor
from database.dbconection import Session
from database.crud import get_all_from_database
from services.check_runner_service import run_monitor_check
import asyncio
import logging
from collections.abc import Callable
from datetime import datetime
import os
from sqlalchemy.orm import Session as OrmSession

logger = logging.getLogger(__name__)

SCHEDULER_INTERVAL = int(os.getenv("SCHEDULER_INTERVAL", 5))

taskScheduler: asyncio.Task | None = None
running_tasks: set[asyncio.Task] = set()
running_monitor_ids: set[int] = set()


async def run_scheduler_loop(
    session_factory: Callable[[], OrmSession] = Session,
    tick_seconds: int = SCHEDULER_INTERVAL,
):
    logger.info("scheduler loop started", extra={"interval_seconds": SCHEDULER_INTERVAL})
    while True:
        try:
            monitors = should_run(session_factory)
            logger.debug("scheduler found monitors ready to check", extra={"count": len(monitors)})
            for monitor in monitors:
                if monitor.id in running_monitor_ids:
                    logger.debug("monitor check already running", extra={"monitor_id": monitor.id})
                    continue
                running_monitor_ids.add(monitor.id)
                task = asyncio.create_task(
                    run_monitor_check(monitor.id, session_factory=session_factory)
                )
                running_tasks.add(task)
                task.add_done_callback(
                    lambda done_task, monitor_id=monitor.id: handle_monitor_task_done(
                        done_task,
                        monitor_id,
                    )
                )
        except Exception:
            logger.exception("scheduler loop failed")
        await asyncio.sleep(tick_seconds)


def should_run(session_factory: Callable[[], OrmSession] = Session) -> list[Monitor]:
    db = session_factory()
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


def handle_monitor_task_done(task: asyncio.Task, monitor_id: int):
    running_tasks.discard(task)
    running_monitor_ids.discard(monitor_id)
    try:
        task.result()
    except asyncio.CancelledError:
        pass
    except Exception:
        logger.exception("Monitor check task failed")

    
def start_scheduler_loop(session_factory: Callable[[], OrmSession] = Session):
    global taskScheduler
    if taskScheduler is None or taskScheduler.done():
        taskScheduler = asyncio.create_task(run_scheduler_loop(session_factory=session_factory))
        logger.info("scheduler task created")


def stop_scheduler_loop():
    global taskScheduler
    if taskScheduler is not None and not taskScheduler.done():
        taskScheduler.cancel()
        logger.info("scheduler task stopped")
    running_tasks.clear()
    running_monitor_ids.clear()
    taskScheduler = None
