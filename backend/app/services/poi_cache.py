import asyncio
import time
from collections import OrderedDict

from app.application.ports import POIPort
from app.domain.schemas import POIInfo

CacheKey = tuple[float, float, int, str]


class CachedPOIService:
    def __init__(
        self,
        service: POIPort,
        ttl: float = 1800.0,
        max_entries: int = 128,
    ):
        if ttl <= 0:
            raise ValueError("TTL must be positive")

        if max_entries <= 0:
            raise ValueError("max_entries must be positive")

        self.service = service
        self.ttl = ttl
        self.max_entries = max_entries

        self.cache: OrderedDict[CacheKey, tuple[float, list[POIInfo]]] = OrderedDict()

        self.in_flight: dict[CacheKey, asyncio.Task[list[POIInfo]]] = {}

        self.lock = asyncio.Lock()

    async def _fetch_and_store(
        self,
        key: CacheKey,
        lat: float,
        lon: float,
        radius: int,
        category: str,
    ) -> list[POIInfo]:
        try:
            pois = await self.service.get_pois(
                lat,
                lon,
                radius,
                category=category,
            )

            async with self.lock:
                self.cache[key] = (
                    time.monotonic() + self.ttl,
                    [poi.model_copy(deep=True) for poi in pois],
                )

                self.cache.move_to_end(key)

                while len(self.cache) > self.max_entries:
                    self.cache.popitem(last=False)

            return pois
        finally:
            async with self.lock:
                self.in_flight.pop(key, None)

    async def get_pois(
        self,
        lat: float,
        lon: float,
        radius: int = 5000,
        category: str = "museum",
    ) -> list[POIInfo]:
        key = (lat, lon, radius, category)

        async with self.lock:
            cached = self.cache.get(key)

            if cached is not None:
                expires_at, pois = cached

                if time.monotonic() < expires_at:
                    self.cache.move_to_end(key)

                    return [poi.model_copy(deep=True) for poi in pois]

                del self.cache[key]

            task = self.in_flight.get(key)

            if task is None:
                task = asyncio.create_task(
                    self._fetch_and_store(
                        key,
                        lat,
                        lon,
                        radius,
                        category,
                    )
                )

                self.in_flight[key] = task

        result = await asyncio.shield(task)

        return [poi.model_copy(deep=True) for poi in result]

    async def get_wikidata_id(
        self,
        place_id: str,
    ) -> str | None:
        return await self.service.get_wikidata_id(place_id)
