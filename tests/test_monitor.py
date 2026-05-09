import pytest_asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager
from main import create_app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.dbconection import get_db, DBaseModel
from database.crud import get_all_from_database
from database.dbmodels import Monitor
import os
from dotenv import load_dotenv
from asyncio import sleep
from schemas.incident import IncidentResponse
from services.check_runner_service import run_monitor_check

load_dotenv()
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_DB_TEST = os.getenv("POSTGRES_DB_TEST", f"{POSTGRES_USER}_TEST")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PORT = os.getenv("DB_PORT_TEST", 5436)
# Create the app with the testing param
app = create_app(testing=True)
# Create a new engine with a test database
engine = create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
                       f"@localhost:{PORT}/{POSTGRES_DB_TEST}")
Session = sessionmaker(bind=engine)
DBaseModel.metadata.create_all(engine)


# Create and override the get_db function to get the database test
def get_db_override():
    db = Session()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = get_db_override


@pytest_asyncio.fixture
async def async_client():
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), 
                               base_url="http://testserver") as client:
            yield client


@pytest.mark.asyncio
async def test_check_if_healthy(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


@pytest.mark.asyncio
async def test_check_if_ready(async_client):
    response = await async_client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


@pytest.mark.asyncio
async def test_post_monitor(async_client):
    monitor_to_post = {  
        "title": "testPost",
        "type": "http",
        "interval_seconds": 5,
        "config": {
            "url": "https://www.google.com.ar",
            "expected_status": 202
        }
    }
    response = await async_client.post("/monitor/", json=monitor_to_post)
    database: list[Monitor] = get_all_from_database(Monitor, Session())
    assert response.status_code == 200
    assert any(monitor.id == response.json().get("id") for monitor in database)


@pytest.mark.asyncio
async def test_succesfull_monitor_check(async_client):
    monitor_to_post = {  
        "title": "testMonitorOk",
        "type": "http",
        "interval_seconds": 3,
        "config": {
            "url": "https://www.google.com",
            "expected_status": 202
        }
    }
    response = await async_client.post("/monitor/", json=monitor_to_post)
    monitor_id = response.json().get("id")
    await sleep(5)
    response = await async_client.get("/incidents")
    incidents: list[dict] = response.json()

    assert not any(incident["monitor_id"] == monitor_id for incident in incidents)


@pytest.mark.asyncio
async def test_failed_monitor_check(async_client):
    monitor_to_post = {  
        "title": "testMonitorFail",
        "type": "http",
        "interval_seconds": 3,
        "config": {
            "url": "https://www.google.com",
            "expected_status": -1
        }
    }
    response = await async_client.post("/monitor/", json=monitor_to_post)
    monitor_id = response.json().get("id")

    await run_monitor_check(monitor_id, db=Session())

    response = await async_client.get("/incidents")
    incidents: list[dict] = response.json()
    assert any(incident["monitor_id"] == monitor_id for incident in incidents)
