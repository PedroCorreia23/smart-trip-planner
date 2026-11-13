from unittest.mock import AsyncMock

import pytest

from app.domain.schemas import POIInfo
from app.exceptions import ExternalServiceError
from app.services.poi_cache import CachedPOIService


def make_poi():
    return POIInfo(
        id="Q2351947",
        wikidata_id="Q2351947",
        name="Sé Velha de Coimbra",
        category="monument",
        lat=40.208561,
        lon=-8.426922,
    )


@pytest.mark.asyncio
async def test_cache_hit_avoids_second_request():
    backend = AsyncMock()
    backend.get_pois.return_value = [make_poi()]

    service = CachedPOIService(backend)

    first = await service.get_pois(40.2033, -8.4103, category="monument")
    second = await service.get_pois(40.2033, -8.4103, category="monument")

    assert first[0].name == second[0].name
    assert backend.get_pois.await_count == 1


@pytest.mark.asyncio
async def test_different_categories_use_different_keys():
    backend = AsyncMock()
    backend.get_pois.return_value = [make_poi()]

    service = CachedPOIService(backend)

    await service.get_pois(40.2033, -8.4103, category="monument")
    await service.get_pois(40.2033, -8.4103, category="museum")

    assert backend.get_pois.await_count == 2


@pytest.mark.asyncio
async def test_cache_expires(monkeypatch):
    clock = {"now": 100.0}

    monkeypatch.setattr(
        "app.services.poi_cache.time.monotonic",
        lambda: clock["now"],
    )

    backend = AsyncMock()
    backend.get_pois.return_value = [make_poi()]

    service = CachedPOIService(backend, ttl=30)

    await service.get_pois(40.2033, -8.4103)

    clock["now"] = 131.0

    await service.get_pois(40.2033, -8.4103)

    assert backend.get_pois.await_count == 2


@pytest.mark.asyncio
async def test_errors_are_not_cached():
    backend = AsyncMock()
    backend.get_pois.side_effect = [
        ExternalServiceError("Unavailable"),
        [make_poi()],
    ]

    service = CachedPOIService(backend)

    with pytest.raises(ExternalServiceError):
        await service.get_pois(40.2033, -8.4103)

    result = await service.get_pois(40.2033, -8.4103)

    assert len(result) == 1
    assert backend.get_pois.await_count == 2


@pytest.mark.asyncio
async def test_cache_respects_max_entries():
    backend = AsyncMock()
    backend.get_pois.return_value = [make_poi()]

    service = CachedPOIService(
        backend,
        max_entries=2,
    )

    for lat in (40.1, 40.2, 40.3):
        await service.get_pois(lat, -8.4)

    assert len(service.cache) == 2
    assert (40.1, -8.4, 5000, "museum") not in service.cache


@pytest.mark.asyncio
async def test_cached_data_is_independent():
    backend = AsyncMock()
    backend.get_pois.return_value = [make_poi()]

    service = CachedPOIService(backend)

    first = await service.get_pois(40.2033, -8.4103)

    first[0].name = "Modified"

    second = await service.get_pois(40.2033, -8.4103)

    assert second[0].name == "Sé Velha de Coimbra"


@pytest.mark.asyncio
async def test_wikidata_id_is_delegated():
    backend = AsyncMock()
    backend.get_wikidata_id.return_value = "Q2351947"

    service = CachedPOIService(backend)

    result = await service.get_wikidata_id("Q2351947")

    assert result == "Q2351947"
    backend.get_wikidata_id.assert_awaited_once_with("Q2351947")


def test_invalid_cache_configuration():
    with pytest.raises(ValueError):
        CachedPOIService(AsyncMock(), ttl=0)

    with pytest.raises(ValueError):
        CachedPOIService(AsyncMock(), max_entries=0)
