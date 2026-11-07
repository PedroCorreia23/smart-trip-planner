from app.application.ports import POIImagePort, POIPort
from app.domain.schemas import POIInfo


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
