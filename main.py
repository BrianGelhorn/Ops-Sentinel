from fastapi import FastAPI
from routers import health, incidents, ready

app = FastAPI()

app.include_router(health.router)
app.include_router(incidents.router)
app.include_router(ready.router)