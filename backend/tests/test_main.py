from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_trip_search_use_case
from app.exceptions import (
    CurrencyUnavailableError,
    ExternalServiceError,
    LocationNotFoundError,
)
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides.clear()


def test_read_main():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_trip_valid():

    payload = {
        "origin": "Lisboa",
        "destination": "New York",
        "start_date": "2026-10-10",
        "end_date": "2026-10-15",
    }

    fake_result = {
        "message": "Trip successfully processed",
        "trip_details": {
            "origin": "Lisboa",
            "destination": "New York",
            "start_date": "2026-10-10",
            "end_date": "2026-10-15",
        },
        "origin_coordinates": {"lat": 38.72, "lon": -9.14, "country_code": "pt"},
        "destination_coordinates": {"lat": 40.71, "lon": -74.00, "country_code": "us"},
        "weather": {
            "time": ["2026-10-10"],
            "temperature_2m_max": [20.0],
            "temperature_2m_min": [10.0],
            "precipitation_sum": [0.0],
        },
        "origin_currency": {"code": "EUR", "name": "Euro", "symbol": "€"},
        "destination_currency": {"code": "USD", "name": "US Dollar", "symbol": "$"},
        "exchange_rate": {"base": "EUR", "target": "USD", "rate": 1.18},
    }

    fake_use_case = AsyncMock()
    fake_use_case.execute.return_value = fake_result

    app.dependency_overrides[get_trip_search_use_case] = lambda: fake_use_case

    response = client.post("/trips/search", json=payload)

    assert response.status_code == 200
    assert response.json() == fake_result

    fake_use_case.execute.assert_awaited_once()


def test_search_trip_invalid_dates():

    payload = {
        "origin": "Lisboa",
        "destination": "Porto",
        "start_date": "2026-10-10",
        "end_date": "2026-10-09",
    }

    response = client.post("/trips/search", json=payload)

    assert response.status_code == 422


def test_search_trip_external_service_error():
    payload = {
        "origin": "Lisboa",
        "destination": "New York",
        "start_date": "2026-10-10",
        "end_date": "2026-10-15",
    }

    fake_use_case = AsyncMock()
    fake_use_case.execute.side_effect = ExternalServiceError("Weather service is unavailable.")

    app.dependency_overrides[get_trip_search_use_case] = lambda: fake_use_case

    response = client.post("/trips/search", json=payload)

    assert response.status_code == 502

    assert response.json() == {"detail": "An external service is currently unavailable."}


def test_search_trip_location_not_found():

    payload = {
        "origin": "CidadeInexistente",
        "destination": "New York",
        "start_date": "2026-10-10",
        "end_date": "2026-10-15",
    }

    fake_use_case = AsyncMock()
    fake_use_case.execute.side_effect = LocationNotFoundError("Origin city not found.")

    app.dependency_overrides[get_trip_search_use_case] = lambda: fake_use_case

    response = client.post("/trips/search", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "Origin city not found."}


def test_search_trip_currency_unavailable():

    payload = {
        "origin": "Lisboa",
        "destination": "New York",
        "start_date": "2026-10-10",
        "end_date": "2026-10-15",
    }

    fake_use_case = AsyncMock()
    fake_use_case.execute.side_effect = CurrencyUnavailableError(
        "Could not retrieve destination currency."
    )

    app.dependency_overrides[get_trip_search_use_case] = lambda: fake_use_case

    response = client.post("/trips/search", json=payload)

    assert response.status_code == 502
    assert response.json() == {"detail": "Could not retrieve destination currency."}
