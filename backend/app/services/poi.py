import logging

import httpx

from app.config import settings
from app.domain.schemas import POIInfo
from app.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class POIService:
    async def get_pois(self, lat: float, lon: float, radius: int = 5000) -> list[POIInfo]:
        url = f"{settings.OVERPASS_BASE_URL}/interpreter"
        headers = {"User-Agent": settings.USER_AGENT}
        query = f"""
            [out:json];
            nwr["tourism"="museum"](around:{radius},{lat},{lon});
            out center;
        """

        try:
            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
                response = await client.post(
                    url,
                    data={"data": query},
                    headers=headers,
                )

                response.raise_for_status()
                data = response.json()

                pois = []

                for element in data["elements"]:
                    name = element.get("tags", {}).get("name")

                    if not name:
                        continue

                    category = element["tags"]["tourism"]

                    if element["type"] == "node":
                        poi_lat = element["lat"]
                        poi_lon = element["lon"]
                    else:
                        center = element.get("center")

                        if not center:
                            continue

                        poi_lat = center["lat"]
                        poi_lon = center["lon"]

                    poi = POIInfo(
                        id=element["id"],
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
            logger.error("POIS API  request failed: %s", exc)
            raise ExternalServiceError("POI service is unavailable.") from exc
