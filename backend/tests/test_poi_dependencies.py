import asyncio
from types import SimpleNamespace

import httpx

from app.dependencies import get_poi_search_use_case
from app.services.poi import POIService
from app.services.poi_cache import CachedPOIService
from app.services.poi_fallback import FallbackPOIService
from app.services.poi_images import POIImageService
from app.services.wikidata_poi import WikidataPOIService


def test_poi_dependencies_reuse_shared_service():
    async def run_test():
        async with httpx.AsyncClient() as client:
            poi_service = FallbackPOIService(
                primary=CachedPOIService(WikidataPOIService(client)),
                fallback=POIService(),
                timeout=7.0,
            )

            request = SimpleNamespace(
                app=SimpleNamespace(
                    state=SimpleNamespace(
                        http_client=client,
                        poi_service=poi_service,
                    )
                )
            )

            first = get_poi_search_use_case(request)
            second = get_poi_search_use_case(request)

            assert first.poi_service is poi_service
            assert second.poi_service is poi_service

            assert isinstance(
                first.poi_service,
                FallbackPOIService,
            )

            assert isinstance(
                first.poi_service.primary,
                CachedPOIService,
            )

            assert isinstance(
                first.poi_service.primary.service,
                WikidataPOIService,
            )

            assert isinstance(
                first.poi_service.fallback,
                POIService,
            )

            assert isinstance(
                first.poi_image_service,
                POIImageService,
            )

            assert first.poi_service.primary.service.client is client

    asyncio.run(run_test())
