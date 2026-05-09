import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient, Request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.crud import get_all_from_database
from database.dbconection import DBaseModel, get_db
from database.dbmodels import Monitor
from main import create_app
from services.check_runner_service import run_monitor_check


@pytest_asyncio.fixture
async def test_app(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/test.db")
    Session = sessionmaker(bind=engine)
    DBaseModel.metadata.create_all(engine)

    app = create_app(
        testing=True,
        session_factory=Session,
        start_scheduler=False,
    )

    async def get_db_override():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = get_db_override
    try:
        yield app, Session
    finally:
        app.dependency_overrides.clear()
        DBaseModel.metadata.drop_all(engine)


@pytest_asyncio.fixture
async def async_client(test_app):
    app, _ = test_app
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client


async def fake_http_get(url: str) -> Response:
    return Response(202, request=Request("GET", url))


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
async def test_post_monitor(async_client, test_app):
    _, Session = test_app
    monitor_to_post = {
        "title": "testPost",
        "type": "http",
        "interval_seconds": 5,
        "config": {
            "url": "https://www.google.com.ar",
            "expected_status": 202,
        },
    }
    response = await async_client.post("/monitor/", json=monitor_to_post)
    db = Session()
    database: list[Monitor] = get_all_from_database(Monitor, db)
    db.close()
    assert response.status_code == 200
    assert any(monitor.id == response.json().get("id") for monitor in database)


@pytest.mark.asyncio
async def test_rejects_invalid_monitor(async_client):
    response = await async_client.post(
        "/monitor/",
        json={
            "title": "invalid",
            "type": "http",
            "interval_seconds": 0,
            "config": {
                "url": "not-a-url",
                "expected_status": 999,
            },
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_successful_monitor_check(async_client, test_app):
    _, Session = test_app
    monitor_to_post = {
        "title": "testMonitorOk",
        "type": "http",
        "interval_seconds": 3,
        "config": {
            "url": "https://www.google.com",
            "expected_status": 202,
        },
    }
    response = await async_client.post("/monitor/", json=monitor_to_post)
    monitor_id = response.json().get("id")
    await run_monitor_check(
        monitor_id,
        session_factory=Session,
        http_get=fake_http_get,
    )
    response = await async_client.get("/incidents")
    incidents = response.json()

    assert not any(incident["monitor_id"] == monitor_id for incident in incidents)


@pytest.mark.asyncio
async def test_failed_monitor_check(async_client, test_app):
    _, Session = test_app
    monitor_to_post = {
        "title": "testMonitorFail",
        "type": "http",
        "interval_seconds": 3,
        "config": {
            "url": "https://www.google.com",
            "expected_status": 204,
        },
    }
    response = await async_client.post("/monitor/", json=monitor_to_post)
    monitor_id = response.json().get("id")

    await run_monitor_check(
        monitor_id,
        session_factory=Session,
        http_get=fake_http_get,
    )

    response = await async_client.get("/incidents")
    incidents = response.json()
    assert any(incident["monitor_id"] == monitor_id for incident in incidents)
