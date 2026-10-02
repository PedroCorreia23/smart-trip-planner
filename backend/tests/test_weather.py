from datetime import date
from unittest.mock import Mock, patch

import httpx
import pytest

from app.domain.schemas import WeatherInfo
from app.exceptions import ExternalServiceError
from app.services.weather import WeatherService


@pytest.mark.asyncio
async def test_get_weather_success():
    fake_api_response = {
        "daily": {
            "time": ["2026-10-10", "2026-10-11"],
            "temperature_2m_max": [22.0, 21.0],
            "temperature_2m_min": [12.0, 11.0],
            "precipitation_sum": [0.0, 2.4],
        }
    }

    mock_response = Mock()
    mock_response.json.return_value = fake_api_response

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        service = WeatherService()

        resultado = await service.get_weather(
            lat=48.8566, lon=2.3522, start_date=date(2026, 10, 10), end_date=date(2026, 10, 11)
        )

    assert resultado == WeatherInfo(
        time=["2026-10-10", "2026-10-11"],
        temperature_2m_max=[22.0, 21.0],
        temperature_2m_min=[12.0, 11.0],
        precipitation_sum=[0.0, 2.4],
    )


@pytest.mark.asyncio
async def test_get_weather_not_found():
    fake_api_response = {}

    mock_response = Mock()
    mock_response.json.return_value = fake_api_response

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        service = WeatherService()

        resultado = await service.get_weather(
            lat=48.8566, lon=2.3522, start_date=date(2026, 10, 10), end_date=date(2026, 10, 11)
        )

    assert resultado is None


@pytest.mark.asyncio
async def test_weather_http_error():
    request = httpx.Request("GET", "https://api.open-meteo.com/v1/forecast")

    response = httpx.Response(500, request=request)

    mock_response = Mock()

    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server error", request=request, response=response
    )

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        service = WeatherService()

        with pytest.raises(ExternalServiceError):
            await service.get_weather(
                lat=48.8566, lon=2.3522, start_date=date(2026, 10, 10), end_date=date(2026, 10, 11)
            )


@pytest.mark.asyncio
async def test_weather_request_error():
    request = httpx.Request(
        "GET",
        "https://api.open-meteo.com/v1/forecast",
    )

    with patch(
        "httpx.AsyncClient.get",
        side_effect=httpx.RequestError("Connection failed", request=request),
    ):
        service = WeatherService()

        with pytest.raises(ExternalServiceError) as exc:
            await service.get_weather(
                lat=48.8566, lon=2.3522, start_date=date(2026, 10, 10), end_date=date(2026, 10, 11)
            )

        assert str(exc.value) == "Weather service is unavailable."
