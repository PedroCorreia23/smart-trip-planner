import logging

import httpx

from app.config import settings
from app.domain.schemas import POIInfo
from app.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

POI_CATEGORIES = {
    "museum": "entertainment.museum",
    "monument": "tourism.sights",
    "park": "leisure.park",
    "attraction": "tourism.attraction",
}


class POIService:
    async def get_pois(self, lat: float, lon: float, radius: int = 5000, category: str = "museum") -> list[POIInfo]:
        url = f"{settings.GEOAPIFY_BASE_URL}/places"
        params = {
            "categories": POI_CATEGORIES[category],
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

    async def get_wikidata_id(self, place_id: str) -> str | None:
        url = f"{settings.GEOAPIFY_BASE_URL}/place-details"
        params = {
            "id": place_id,
            "apiKey": settings.GEOAPIFY_API_KEY,
        }

        try:
            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            for feature in data.get("features", []):
                properties = feature.get("properties", {})

                if properties.get("feature_type") != "details":
                    continue

                wiki_data = properties.get("wiki_and_media") or {}
                wikidata = wiki_data.get("wikidata")

                if wikidata:
                    return wikidata

            return None

        except httpx.HTTPStatusError as exc:
            logger.error(
                "Geoapify Place Details returned HTTP error: status=%s",
                exc.response.status_code,
            )
            raise ExternalServiceError("Geoapify Place Details returned an HTTP error.") from exc

        except httpx.RequestError as exc:
            logger.error(
                "Geoapify Place Details request failed: type=%s error=%r",
                type(exc).__name__,
                exc,
            )
            raise ExternalServiceError("Geoapify Place Details service is unavailable.") from exc
