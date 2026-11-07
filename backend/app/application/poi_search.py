import logging

from app.application.ports import POIPort, POIImagePort
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

    async def execute(self, lat: float, lon: float, radius: int = 5000) -> list[POIInfo]:
        return await self.poi_service.get_pois(lat, lon, radius)

    async def enrich_poi(self, poi: POIInfo) -> POIInfo:
        try:
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
                update={"image_url": image.thumbnail_url or image.url}
            )

        except ExternalServiceError as exc:
            logger.warning(
                "Could not enrich POI %s with an image: %s",
                poi.id,
                exc,
            )
            return poi