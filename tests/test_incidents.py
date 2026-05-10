import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.dbconection import DBaseModel, get_db
from main import create_app


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
        yield app
    finally:
        app.dependency_overrides.clear()
        DBaseModel.metadata.drop_all(engine)


@pytest_asyncio.fixture
async def async_client(test_app):
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://testserver",
    ) as client:
        yield client


def incident_payload(resolution: dict) -> dict:
    return {
        "monitor_id": None,
        "title": "API latency degraded",
        "service": "payments-api",
        "type": "http",
        "severity": "high",
        "summary": "The payments API is responding slowly.",
        "source": "synthetic-monitor",
        "trigger": {
            "type": "status_code",
            "expected_status": 200,
            "observed_status": 500,
            "failed_attempts": 3,
        },
        "evidence": {
            "response_time_in_ms": 2500,
            "last_cpu_usage_percent": 91.5,
            "last_memory_usage_percent": 82.0,
            "error_message": "Unexpected HTTP 500",
        },
        "resolution": resolution,
    }


@pytest.mark.asyncio
async def test_post_incident_accepts_complete_resolution(async_client):
    payload = incident_payload(
        {
            "action_taken": "Restarted the payments worker pool",
            "action_result": "Service recovered",
            "date": "2026-05-10T12:00:00Z",
        }
    )

    response = await async_client.post("/incidents/", json=payload)

    assert response.status_code == 201
    assert response.json()["resolution"] == payload["resolution"]


@pytest.mark.asyncio
async def test_post_incident_accepts_incomplete_resolution(async_client):
    payload = incident_payload(
        {
            "action_taken": "Acknowledged by on-call engineer",
        }
    )

    response = await async_client.post("/incidents/", json=payload)

    assert response.status_code == 201
    assert response.json()["resolution"] == {
        "action_taken": "Acknowledged by on-call engineer",
        "action_result": None,
        "date": None,
    }


@pytest.mark.asyncio
async def test_post_incident_accepts_empty_resolution(async_client):
    response = await async_client.post("/incidents/", json=incident_payload({}))

    assert response.status_code == 201
    assert response.json()["resolution"] == {
        "action_taken": None,
        "action_result": None,
        "date": None,
    }


@pytest.mark.asyncio
async def test_post_incident_rejects_invalid_resolution_with_422(async_client):
    payload = incident_payload(
        {
            "action_taken": {"not": "a string"},
            "action_result": "Ignored because payload is invalid",
            "date": "2026-05-10T12:00:00Z",
        }
    )

    response = await async_client.post("/incidents/", json=payload)

    assert response.status_code == 422
