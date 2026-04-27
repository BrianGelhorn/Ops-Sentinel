import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_check_if_healthy():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

def test_