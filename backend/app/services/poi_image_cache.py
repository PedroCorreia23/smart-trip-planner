import asyncio
import copy
import time
from collections import OrderedDict

from app.application.ports import POIImagePort
from app.domain.schemas import POIImageInfo

CacheKey = tuple[str, str]
CacheValue = str | POIImageInfo | None


class CachedPOIImageService:
    def __init__(
        self,
        service: POIImagePort,
        ttl: float = 1800.0,
        max_entries: int = 256,
    ):
        if ttl <= 0:
            raise ValueError("TTL must be positive")

        if max_entries <= 0:
            raise ValueError("max_entries must be positive")

        self.service = service
        self.ttl = ttl
        self.max_entries = max_entries

        self.cache: OrderedDict[
            CacheKey,
            tuple[float, CacheValue],
        ] = OrderedDict()

        self.lock = asyncio.Lock()

    async def _get_cached(
        self,
        key: CacheKey,
    ) -> tuple[bool, CacheValue]:
        async with self.lock:
            cached = self.cache.get(key)

            if cached is None:
                return False, None

            expires_at, value = cached

            if time.monotonic() >= expires_at:
                del self.cache[key]
                return False, None

            self.cache.move_to_end(key)

            return True, copy.deepcopy(value)

    async def _store(
        self,
        key: CacheKey,
        value: CacheValue,
    ) -> None:
        async with self.lock:
            self.cache[key] = (
                time.monotonic() + self.ttl,
                copy.deepcopy(value),
            )

            self.cache.move_to_end(key)

            while len(self.cache) > self.max_entries:
                self.cache.popitem(last=False)

    async def get_image(
        self,
        wikidata_id: str,
    ) -> str | None:
        key = ("wikidata", wikidata_id)

        found, cached = await self._get_cached(key)

        if found:
            if isinstance(cached, str):
                return cached

            return None

        filename = await self.service.get_image(wikidata_id)

        await self._store(key, filename)

        return filename

    async def get_commons_image(
        self,
        filename: str,
    ) -> POIImageInfo | None:
        key = ("commons", filename)

        found, cached = await self._get_cached(key)

        if found:
            if isinstance(cached, POIImageInfo):
                return cached

            return None

        image = await self.service.get_commons_image(filename)

        await self._store(key, image)

        return image
