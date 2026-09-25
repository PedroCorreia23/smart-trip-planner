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

    # 2. Intercetamos o get_coordinates para ele não ir à Internet
    with patch("app.main.GeocodingService.get_coordinates", new_callable=AsyncMock) as mock_geo:
        # Definimos as coordenadas falsas que o serviço deve devolver instantaneamente
        mock_geo.return_value = {"lat": 48.8534, "lon": 2.3483}
        
        # 3. Fazemos o pedido com o payload
        response = client.post("/trips/search", json=payload)
        
        # 4. Validamos se o status é 200 e se o JSON tem a estrutura nova
        assert response.status_code == 200
        assert response.json()["destination_coordinates"] == {"lat": 48.8534, "lon": 2.3483}


def test_search_trip_invalid_dates():

    payload = {
        "origin": "Lisboa",
        "destination": "Porto",
        "start_date": "2026-10-10",
        "end_date": "2026-10-9"
    }

    response = client.post("/trips/search", json=payload)
    assert response.status_code == 422

    
