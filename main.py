from fastapi import FastAPI
from routers import health, incidents, ready, monitors
from database.dbconection import engine, DBaseModel
from contextlib import asynccontextmanager
from workers.scheduler import start_scheduler_loop
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    DBaseModel.metadata.create_all(engine)
    start_scheduler_loop()
    yield
    pass

app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(incidents.router)
app.include_router(ready.router)
app.include_router(monitors.router)