import logging

import httpx

from app.config import settings
from app.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

class POIService:
    async def get_pois(self, lat: float, lon: float, radius: int = 5000):
        url = f"{settings.OVERPASS_BASE_URL}/interpreter"
        headers = {"User-Agent": settings.USER_AGENT}

        try:
            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
                response = await client.post(url, {"data": query})
                response.raise_for_status()
                data = response.json()

        except httpx.HTTPStatusError as exc:
                    logger.error("POIS API returned HTTP error: status=%s", exc.response.status_code)
                    raise ExternalServiceError("POIS service returned an HTTP error.") from exc