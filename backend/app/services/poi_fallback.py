import asyncio
import logging

from app.application.ports import POIPort
from app.domain.schemas import POIInfo
from app.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class FallbackPOIService:
    def __init__(
        self,
        primary: POIPort,
        fallback: POIPort,
        timeout: float = 7.0,
    ):
        if timeout <= 0:
            raise ValueError("Timeout must be positive")

        self.primary = primary
        self.fallback = fallback
        self.timeout = timeout

    async def get_pois(
        self,
        lat: float,
        lon: float,
        radius: int = 5000,
        category: str = "museum",
    ) -> list[POIInfo]:
        try:
            pois = await asyncio.wait_for(
                self.primary.get_pois(
                    lat,
                    lon,
                    radius,
                    category=category,
                ),
                timeout=self.timeout,
            )

            if pois:
                return pois

            logger.info("Primary POI service returned no results. Using fallback.")

        except TimeoutError:
            logger.warning(
                "Primary POI service timed out after %.1fs. Using fallback.",
                self.timeout,
            )

        except ExternalServiceError as exc:
            logger.warning(
                "Primary POI service failed: %s. Using fallback.",
                exc,
            )

        return await self.fallback.get_pois(
            lat,
            lon,
            radius,
            category=category,
        )

    async def get_wikidata_id(
        self,
        place_id: str,
    ) -> str | None:
        if place_id.startswith("Q") and place_id[1:].isdigit():
            return place_id

        return await self.fallback.get_wikidata_id(place_id)
