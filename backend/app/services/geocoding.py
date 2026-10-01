import logging

import httpx

from app.config import settings
from app.domain.schemas import Coordinates
from app.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class GeocodingService:
    async def get_coordinates(self, city_name: str):
        url = f"{settings.NOMINATIM_BASE_URL}/search?q={city_name}&format=json&limit=1&addressdetails=1"
        headers = {"User-Agent": settings.USER_AGENT}

        try:
            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                if not data:
                    return None  # Caso a cidade não seja encontrada

                latitude = float(data[0]["lat"])
                longitude = float(data[0]["lon"])
                country_code = data[0]["address"]["country_code"]

                return Coordinates(lat=latitude, lon=longitude, country_code=country_code)

        except httpx.HTTPStatusError as exc:
            logger.error("Geocoding API returned HTTP error: status=%s", exc.response.status_code)
            raise ExternalServiceError("Geocoding service returned an HTTP error.") from exc
        except httpx.RequestError as exc:
            logger.error("Geocoding API  request failed: %s", exc)
            raise ExternalServiceError("Geocoding service is unavailable.") from exc
