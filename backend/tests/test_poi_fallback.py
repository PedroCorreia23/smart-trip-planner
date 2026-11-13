import asyncio
from unittest.mock import AsyncMock

import pytest

from app.domain.schemas import POIInfo
from app.exceptions import ExternalServiceError
from app.services.poi_fallback import FallbackPOIService


def make_poi(poi_id="Q19675"):
    return POIInfo(
        id=poi_id,
        wikidata_id=poi_id,
        name="Museu do Louvre",
        category="museum",
        lat=48.8611,
        lon=2.3358,
    )


@pytest.mark.asyncio
async def test_primary_service_success():
    primary = AsyncMock()
    fallback = AsyncMock()

    primary.get_pois.return_value = [make_poi()]

    service = FallbackPOIService(primary, fallback)

    result = await service.get_pois(48.8566, 2.3522, category="museum")

    assert len(result) == 1
    assert result[0].id == "Q19675"
    fallback.get_pois.assert_not_awaited()


@pytest.mark.asyncio
async def test_fallback_when_primary_empty():
    primary = AsyncMock()
    fallback = AsyncMock()

    primary.get_pois.return_value = []
    fallback.get_pois.return_value = [make_poi("geoapify-123")]

    service = FallbackPOIService(primary, fallback)

    result = await service.get_pois(40.2033, -8.4103, category="park")

    assert len(result) == 1
    assert result[0].id == "geoapify-123"

    fallback.get_pois.assert_awaited_once_with(40.2033, -8.4103, 5000, category="park")


@pytest.mark.asyncio
async def test_fallback_when_primary_fails():
    primary = AsyncMock()
    fallback = AsyncMock()

    primary.get_pois.side_effect = ExternalServiceError("Wikidata unavailable")
    fallback.get_pois.return_value = [make_poi()]

    service = FallbackPOIService(primary, fallback)

    result = await service.get_pois(48.8566, 2.3522)

    assert len(result) == 1
    fallback.get_pois.assert_awaited_once()


@pytest.mark.asyncio
async def test_fallback_when_primary_times_out():
    primary = AsyncMock()
    fallback = AsyncMock()

    async def slow_primary(*args, **kwargs):
        await asyncio.sleep(1)
        return [make_poi()]

    primary.get_pois.side_effect = slow_primary
    fallback.get_pois.return_value = [make_poi()]

    service = FallbackPOIService(
        primary,
        fallback,
        timeout=0.01,
    )

    result = await service.get_pois(48.8566, 2.3522)

    assert len(result) == 1
    fallback.get_pois.assert_awaited_once()


@pytest.mark.asyncio
async def test_wikidata_id_is_preserved():
    primary = AsyncMock()
    fallback = AsyncMock()

    service = FallbackPOIService(primary, fallback)

    result = await service.get_wikidata_id("Q19675")

    assert result == "Q19675"
    fallback.get_wikidata_id.assert_not_awaited()


@pytest.mark.asyncio
async def test_geoapify_id_is_resolved():
    primary = AsyncMock()
    fallback = AsyncMock()

    fallback.get_wikidata_id.return_value = "Q19675"

    service = FallbackPOIService(primary, fallback)

    result = await service.get_wikidata_id("geoapify-123")

    assert result == "Q19675"

    fallback.get_wikidata_id.assert_awaited_once_with("geoapify-123")


def test_rejects_invalid_timeout():
    with pytest.raises(ValueError):
        FallbackPOIService(
            AsyncMock(),
            AsyncMock(),
            timeout=0,
        )
