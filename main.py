from fastapi import FastAPI
from routers import health, incidents, ready, monitors
from database.dbconection import Session
from contextlib import asynccontextmanager
from workers.scheduler import start_scheduler_loop, stop_scheduler_loop


def create_app(
    testing: bool = False,
    session_factory=Session,
    start_scheduler: bool = True,
):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if start_scheduler:
            start_scheduler_loop(session_factory=session_factory)
        yield
        if start_scheduler:
            stop_scheduler_loop()
    app = FastAPI(lifespan=lifespan)
    app.include_router(health.router)
    app.include_router(incidents.router)
    app.include_router(ready.router)
    app.include_router(monitors.router)
    return app


app = create_app()
