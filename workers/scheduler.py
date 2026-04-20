from database.dbmodels import Monitor
import asyncio

taskList: dict[int, asyncio.Task] = {}

async def run_scheduler_monitor():
    while True:
        await run_pending_tasks()
        await asyncio.sleep(5)


async def run_pending_tasks():


def add_task(task):
    taskList.