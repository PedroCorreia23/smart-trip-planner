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
        self.in_flight: dict[
            CacheKey,
            asyncio.Task[CacheValue],
        ] = {}

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
            return self._get_cached_unlocked(key)

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
            return cached if isinstance(cached, str) else None

        async with self.lock:
            found, cached = self._get_cached_unlocked(key)

            if found:
                return cached if isinstance(cached, str) else None

            task = self.in_flight.get(key)

            if task is None:
                task = asyncio.create_task(self._fetch_image(key, wikidata_id))
                self.in_flight[key] = task

        filename = await asyncio.shield(task)

        return filename

    async def get_commons_image(
        self,
        filename: str,
    ) -> POIImageInfo | None:
        key = ("commons", filename)

        found, cached = await self._get_cached(key)

        if found:
            return cached if isinstance(cached, POIImageInfo) else None

        async with self.lock:
            found, cached = self._get_cached_unlocked(key)

            if found:
                return cached if isinstance(cached, POIImageInfo) else None

            task = self.in_flight.get(key)

            if task is None:
                task = asyncio.create_task(self._fetch_commons_image(key, filename))
                self.in_flight[key] = task

        image = await asyncio.shield(task)

        return image

    async def _fetch_image(
        self,
        key: CacheKey,
        wikidata_id: str,
    ) -> str | None:
        try:
            filename = await self.service.get_image(wikidata_id)

            await self._store(key, filename)

            return filename
        finally:
            async with self.lock:
                self.in_flight.pop(key, None)

    def _get_cached_unlocked(
        self,
        key: CacheKey,
    ) -> tuple[bool, CacheValue]:
        cached = self.cache.get(key)

        if cached is None:
            return False, None

        expires_at, value = cached

        if time.monotonic() >= expires_at:
            del self.cache[key]
            return False, None

        self.cache.move_to_end(key)

        return True, copy.deepcopy(value)

    async def _fetch_commons_image(
        self,
        key: CacheKey,
        filename: str,
    ) -> POIImageInfo | None:
        try:
            image = await self.service.get_commons_image(filename)

            await self._store(key, image)

            return image
        finally:
            async with self.lock:
                self.in_flight.pop(key, None)
