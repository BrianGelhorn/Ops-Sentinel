import asyncio

import pytest

from workers import scheduler


@pytest.mark.asyncio
async def test_stop_scheduler_loop_cancels_running_tasks():
    scheduler.running_tasks.clear()
    scheduler.running_monitor_ids.clear()
    scheduler.taskScheduler = None

    async def fake_monitor_check():
        await asyncio.Event().wait()

    tasks = {asyncio.create_task(fake_monitor_check()) for _ in range(2)}
    scheduler.running_tasks.update(tasks)
    scheduler.running_monitor_ids.update({1, 2})

    await scheduler.stop_scheduler_loop()

    assert all(task.cancelled() for task in tasks)
    assert scheduler.running_tasks == set()
    assert scheduler.running_monitor_ids == set()
    assert scheduler.taskScheduler is None
