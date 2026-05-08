import pytest
from fastapi.testclient import TestClient
from main import create_app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.dbconection import get_db, DBaseModel
from database.crud import get_all_from_database
from database.dbmodels import Monitor
import os
from dotenv import load_dotenv

load_dotenv()
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_DB_TEST = os.getenv("POSTGRES_DB_TEST", f"{POSTGRES_USER}_TEST")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PORT = os.getenv("DB_PORT_TEST", 5436)
# Create the app with the testing param
app = create_app(testing=True)
client = TestClient(app)
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


def test_check_if_healthy():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_check_if_ready():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_post_monitor():
    monitor_to_post = {  
        "title": "testPost",
        "type": "http",
        "interval_seconds": 5,
        "config": {
            "url": "https://www.google.com.ar",
            "expected_status": 202
        }
    }
    response = client.post("/monitor/", json=monitor_to_post)
    database: list[Monitor] = get_all_from_database(Monitor, Session())
    assert response.status_code == 200
    assert any(monitor.id == response.json().get("id") for monitor in database)