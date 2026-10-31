import logging

import httpx

from app.config import settings
from app.domain.schemas import POIInfo
from app.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class POIService:
    async def get_pois(self, lat: float, lon: float, radius: int = 5000) -> list[POIInfo]:
        url = f"{settings.GEOAPIFY_BASE_URL}/places"
        params = {
            "categories": "entertainment.museum",
            "filter": f"circle:{lon},{lat},{radius}",
            "limit": 20,
            "apiKey": settings.GEOAPIFY_API_KEY,
        }

        try:
            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
                response = await client.get(url, params=params)

                response.raise_for_status()
                data = response.json()

                pois = []

                for feature in data["features"]:
                    properties = feature.get("properties", {})

                    name = properties.get("name")

                    if not name:
                        continue

                    place_id = properties.get("place_id")
                    poi_lat = properties.get("lat")
                    poi_lon = properties.get("lon")

                    if not place_id or poi_lat is None or poi_lon is None:
                        continue

                    categories = properties.get("categories", [])
                    category = categories[0] if categories else "unknown"

                    poi = POIInfo(
                        id=place_id,
                        name=name,
                        category=category,
                        lat=poi_lat,
                        lon=poi_lon,
                    )

                    pois.append(poi)

                return pois

        except httpx.HTTPStatusError as exc:
            logger.error("POIS API returned HTTP error: status=%s", exc.response.status_code)
            raise ExternalServiceError("POIS service returned an HTTP error.") from exc
        except httpx.RequestError as exc:
            logger.error(
                "POI API request failed: type=%s error=%r",
                type(exc).__name__,
                exc,
            )
            raise ExternalServiceError("POI service is unavailable.") from exc
