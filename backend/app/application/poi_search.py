import asyncio
import logging

from app.application.ports import POIImagePort, POIPort
from app.domain.schemas import POIInfo
from app.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class POISearchUseCase:
    def __init__(
        self,
        poi_service: POIPort,
        poi_image_service: POIImagePort,
    ):
        self.poi_service = poi_service
        self.poi_image_service = poi_image_service

    async def execute(
        self, lat: float, lon: float, radius: int = 5000, category: str = "museum"
    ) -> list[POIInfo]:
        pois = await self.poi_service.get_pois(lat, lon, radius, category=category)

        semaphore = asyncio.Semaphore(3)

        enriched_pois = await asyncio.gather(
            *(self.enrich_poi_limited(poi, semaphore) for poi in pois[:5])
        )

        enriched_pois.extend(pois[5:])

        return enriched_pois

    async def enrich_poi_limited(self, poi: POIInfo, semaphore: asyncio.Semaphore) -> POIInfo:
        async with semaphore:
            return await self.enrich_poi(poi)

    async def enrich_poi(self, poi: POIInfo) -> POIInfo:
        try:
            wikidata_id = poi.wikidata_id

            if not wikidata_id:
                wikidata_id = poi.wikidata_id

                if not wikidata_id:
                    wikidata_id = await self.poi_service.get_wikidata_id(poi.id)

            if not wikidata_id:
                return poi

            filename = await self.poi_image_service.get_image(wikidata_id)

            if not filename:
                return poi

            image = await self.poi_image_service.get_commons_image(filename)

            if not image:
                return poi

            return poi.model_copy(
                update={
                    "image_url": image.thumbnail_url or image.url,
                    "image_author": image.author,
                    "image_license": image.license,
                    "image_source_url": image.description_url,
                }
            )

        except ExternalServiceError as exc:
            logger.warning(
                "Could not enrich POI %s with an image: %s",
                poi.id,
                exc,
            )
            return poi
