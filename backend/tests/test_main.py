from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status" : "ok"}

def test_search_trip_valid():

    payload = {
        "origin": "Lisboa",
        "destination": "Porto",
        "start_date": "2026-10-10",
        "end_date": "2026-10-15"
    }

    response = client.post("/trips/search", json=payload)
    assert response.status_code == 200

def test_search_trip_invalid_dates():

    payload = {
        "origin": "Lisboa",
        "destination": "Porto",
        "start_date": "2026-10-10",
        "end_date": "2026-10-9"
    }

    response = client.post("/trips/search", json=payload)
    assert response.status_code == 422

    
