import httpx, logging
from datetime import date
from app.exceptions import ExternalServiceError
from app.domain.schemas import WeatherInfo
from app.config import settings

logger = logging.getLogger(__name__)

class WeatherService:

    async def get_weather(self, lat: float, lon: float, start_date: date, end_date: date):
        # A API do Open-Meteo exige as datas no formato ISO (YYYY-MM-DD), o que o tipo 'date' do Python já faz nativamente.
        url = (
            f"{settings.WEATHER_BASE_URL}/v1/forecast?"
            f"latitude={lat}&longitude={lon}&"
            f"start_date={start_date}&end_date={end_date}&"
            f"daily=temperature_2m_max,temperature_2m_min,precipitation_sum&"
            f"timezone=auto"
        )

        try:
            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                if "daily" not in data:
                    return None
                
                daily = data["daily"]
                return WeatherInfo(
                    time=daily["time"],
                    temperature_2m_max=daily[
                        "temperature_2m_max"
                    ],
                    temperature_2m_min=daily[
                        "temperature_2m_min"
                    ],
                    precipitation_sum=daily[
                        "precipitation_sum"
                    ]
                )

        except httpx.HTTPStatusError as exc:
            logger.error("Weather API returned HTTP error: status=%s", exc.response.status_code)
            raise ExternalServiceError("Weather service returned an HTTP error.") from exc
        except httpx.RequestError as exc:
            logger.error("Weather API  request failed: %s", exc)
            raise ExternalServiceError("Weather service is unavailable.") from exc