import pytest, httpx
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from app.main import app
from app.exceptions import ExternalServiceError, LocationNotFoundError, CurrencyUnavailableError
from app.services.exchange_rate import ExchangeRateService

client = TestClient(app)


def test_read_main():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_trip_valid():

    payload = {
        "origin": "Lisboa",
        "destination": "New York",
        "start_date": "2026-10-10",
        "end_date": "2026-10-15"
    }

    fake_result = {
        "message": "Trip successfully processed",
        "trip_details": {
            "origin": "Lisboa",
            "destination": "New York",
            "start_date": "2026-10-10",
            "end_date": "2026-10-15"
        },
        "origin_coordinates": {
            "lat": 38.72,
            "lon": -9.14,
            "country_code": "pt"
        },
        "destination_coordinates": {
            "lat": 40.71,
            "lon": -74.00,
            "country_code": "us"
        },
        "weather": {
            "time": ["2026-10-10"],
            "temperature_2m_max": [20.0],
            "temperature_2m_min": [10.0],
            "precipitation_sum": [0.0]
        },
        "origin_currency": {
            "code": "EUR",
            "name": "Euro",
            "symbol": "€"
        },
        "destination_currency": {
            "code": "USD",
            "name": "US Dollar",
            "symbol": "$"
        },
        "exchange_rate": {
            "base": "EUR",
            "target": "USD",
            "rate": 1.18
        }
    }

    with patch(
        "app.main.TripSearchUseCase.execute",
        return_value=fake_result
    ) as mock_execute:

        response = client.post("/trips/search", json=payload)

    assert response.status_code == 200
    assert response.json() == fake_result

    mock_execute.assert_awaited_once()


def test_search_trip_invalid_dates():

    payload = {
        "origin": "Lisboa",
        "destination": "Porto",
        "start_date": "2026-10-10",
        "end_date": "2026-10-09"
    }

    response = client.post("/trips/search", json=payload)

    assert response.status_code == 422

def test_search_trip_external_service_error():
    payload = {
        "origin": "Lisboa",
        "destination": "New York",
        "start_date": "2026-10-10",
        "end_date": "2026-10-15"
    }

    with patch(
        "app.main.TripSearchUseCase.execute",
        side_effect=ExternalServiceError(
            "Weather service is unavailable."
        )
    ):
        response = client.post(
            "/trips/search",
            json=payload
        )

    assert response.status_code == 502

    assert response.json() == {
        "detail": "An external service is currently unavailable."
    }

def test_search_trip_location_not_found():

    payload = {
        "origin": "CidadeInexistente",
        "destination": "New York",
        "start_date": "2026-10-10",
        "end_date": "2026-10-15"
    }

    with patch(
        "app.main.TripSearchUseCase.execute",
        side_effect=LocationNotFoundError("Origin city not found.")
    ):
        response = client.post("/trips/search", json=payload)

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Origin city not found."
    }

def test_search_trip_currency_unavailable():

    payload = {
        "origin": "Lisboa",
        "destination": "New York",
        "start_date": "2026-10-10",
        "end_date": "2026-10-15"
    }

    with patch(
        "app.main.TripSearchUseCase.execute",
        side_effect=CurrencyUnavailableError(
            "Could not retrieve destination currency."
        )
    ):
        response = client.post("/trips/search", json=payload)

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Could not retrieve destination currency."
    }