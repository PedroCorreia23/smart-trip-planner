import httpx
from datetime import date
from app.exceptions import ExternalServiceError


class WeatherService:
    async def get_weather(self, lat: float, lon: float, start_date: date, end_date: date):
        # A API do Open-Meteo exige as datas no formato ISO (YYYY-MM-DD), o que o tipo 'date' do Python já faz nativamente.
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&"
            f"start_date={start_date}&end_date={end_date}&"
            f"daily=temperature_2m_max,temperature_2m_min,precipitation_sum&"
            f"timezone=auto"
        )

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                if "daily" in data:
                    return data["daily"]
                else:
                    return None
        except httpx.HTTPStatusError as exc:
            raise ExternalServiceError("Weather service returned an HTTP error.") from exc
        except httpx.RequestError as exc:
            raise ExternalServiceError("Weather service is unavailable.") from exc