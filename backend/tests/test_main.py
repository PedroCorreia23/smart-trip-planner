from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import AsyncMock, patch

client = TestClient(app)

def test_read_main():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status" : "ok"}

def test_search_trip_valid():

    payload = {
        "origin": "Lisboa",
        "destination": "Paris",
        "start_date": "2026-10-10",
        "end_date": "2026-10-15"
    }

    fake_coords = {"lat": 48.85, "lon": 2.35}

    fake_weather = {
        "time": ["2026-09-25", "2026-09-26"],
        "temperature_2m_max": [25.0, 22.0],
        "temperature_2m_min": [15.0, 14.0],
        "precipitation_sum": [0.0, 1.2]
    }

    # 2. Intercetamos o get_coordinates para ele não ir à Internet
    with patch("app.main.GeocodingService.get_coordinates", return_value=fake_coords),\
         patch("app.main.WeatherService.get_weather", return_value=fake_weather):
        
            # 3. Fazemos o pedido com o payload
            response = client.post("/trips/search", json=payload)
        
        # 4. Validamos se o status é 200 e se o JSON tem a estrutura nova
    assert response.status_code == 200
    data = response.json()
    assert data["destination_coordinates"] == fake_coords
    assert data["weather"] == fake_weather
    assert data["trip_details"]["destination"] == "Paris"


def test_search_trip_invalid_dates():

    payload = {
        "origin": "Lisboa",
        "destination": "Porto",
        "start_date": "2026-10-10",
        "end_date": "2026-10-9"
    }

    response = client.post("/trips/search", json=payload)
    assert response.status_code == 422

    
