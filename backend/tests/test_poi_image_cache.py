import asyncio
from unittest.mock import AsyncMock

import pytest

from app.domain.schemas import POIImageInfo
from app.exceptions import ExternalServiceError
from app.services.poi_image_cache import CachedPOIImageService


def make_image():
    return POIImageInfo(
        url="https://commons.wikimedia.org/example.jpg",
        thumbnail_url="https://commons.wikimedia.org/thumb.jpg",
        author="Example Author",
        license="CC BY 4.0",
        description_url="https://commons.wikimedia.org/wiki/File:Example.jpg",
    )


@pytest.mark.asyncio
async def test_wikidata_image_is_cached():
    backend = AsyncMock()
    backend.get_image.return_value = "example.jpg"

    service = CachedPOIImageService(backend)

    first = await service.get_image("Q2351947")
    second = await service.get_image("Q2351947")

    assert first == second == "example.jpg"
    backend.get_image.assert_awaited_once_with("Q2351947")


@pytest.mark.asyncio
async def test_commons_metadata_is_cached():
    backend = AsyncMock()
    backend.get_commons_image.return_value = make_image()

    service = CachedPOIImageService(backend)

    first = await service.get_commons_image("example.jpg")
    second = await service.get_commons_image("example.jpg")

    assert first.author == "Example Author"
    assert second.license == "CC BY 4.0"

    backend.get_commons_image.assert_awaited_once_with("example.jpg")


@pytest.mark.asyncio
async def test_missing_image_is_cached():
    backend = AsyncMock()
    backend.get_image.return_value = None

    service = CachedPOIImageService(backend)

    assert await service.get_image("Q1580762") is None
    assert await service.get_image("Q1580762") is None

    backend.get_image.assert_awaited_once()


@pytest.mark.asyncio
async def test_cache_expires(monkeypatch):
    clock = {"now": 100.0}

    monkeypatch.setattr(
        "app.services.poi_image_cache.time.monotonic",
        lambda: clock["now"],
    )

    backend = AsyncMock()
    backend.get_image.return_value = "example.jpg"

    service = CachedPOIImageService(
        backend,
        ttl=30,
    )

    await service.get_image("Q2351947")

    clock["now"] = 131.0

    await service.get_image("Q2351947")

    assert backend.get_image.await_count == 2


@pytest.mark.asyncio
async def test_errors_are_not_cached():
    backend = AsyncMock()

    backend.get_image.side_effect = [
        ExternalServiceError("Unavailable"),
        "example.jpg",
    ]

    service = CachedPOIImageService(backend)

    with pytest.raises(ExternalServiceError):
        await service.get_image("Q2351947")

    result = await service.get_image("Q2351947")

    assert result == "example.jpg"
    assert backend.get_image.await_count == 2


@pytest.mark.asyncio
async def test_cached_metadata_is_independent():
    backend = AsyncMock()
    backend.get_commons_image.return_value = make_image()

    service = CachedPOIImageService(backend)

    first = await service.get_commons_image("example.jpg")

    first.author = "Modified"

    second = await service.get_commons_image("example.jpg")

    assert second.author == "Example Author"


@pytest.mark.asyncio
async def test_cache_respects_max_entries():
    backend = AsyncMock()
    backend.get_image.return_value = "example.jpg"

    service = CachedPOIImageService(
        backend,
        max_entries=2,
    )

    await service.get_image("Q1")
    await service.get_image("Q2")
    await service.get_image("Q3")

    assert len(service.cache) == 2
    assert ("wikidata", "Q1") not in service.cache


@pytest.mark.asyncio
async def test_cache_separates_image_sources():
    backend = AsyncMock()
    backend.get_image.return_value = "example.jpg"
    backend.get_commons_image.return_value = make_image()

    service = CachedPOIImageService(backend)

    await service.get_image("example.jpg")
    await service.get_commons_image("example.jpg")

    assert len(service.cache) == 2
    assert ("wikidata", "example.jpg") in service.cache
    assert ("commons", "example.jpg") in service.cache


def test_invalid_configuration():
    with pytest.raises(ValueError):
        CachedPOIImageService(
            AsyncMock(),
            ttl=0,
        )

    with pytest.raises(ValueError):
        CachedPOIImageService(
            AsyncMock(),
            max_entries=0,
        )


@pytest.mark.asyncio
async def test_concurrent_image_requests():
    backend = AsyncMock()
    calls = 0

    async def slow_backend(*args, **kwargs):
        nonlocal calls

        calls += 1
        await asyncio.sleep(0.05)

        return "example.jpg"

    backend.get_image.side_effect = slow_backend

    service = CachedPOIImageService(backend)

    results = await asyncio.gather(
        service.get_image("Q2351947"),
        service.get_image("Q2351947"),
    )

    assert results == ["example.jpg", "example.jpg"]
    assert calls == 1


@pytest.mark.asyncio
async def test_rechecks_cache_before_creating_task():
    backend = AsyncMock()
    backend.get_image.return_value = "example.jpg"

    service = CachedPOIImageService(backend)

    original_get_cached = service._get_cached
    injected = False

    async def get_cached_with_interleaving(key):
        nonlocal injected

        result = await original_get_cached(key)

        if not injected and not result[0]:
            injected = True
            await service._store(key, "example.jpg")

        return result

    service._get_cached = get_cached_with_interleaving

    result = await service.get_image("Q2351947")

    assert result == "example.jpg"
    backend.get_image.assert_not_awaited()


@pytest.mark.asyncio
async def test_concurrent_commons_requests():
    backend = AsyncMock()
    calls = 0

    async def slow_backend(*args, **kwargs):
        nonlocal calls

        calls += 1
        await asyncio.sleep(0.05)

        return make_image()

    backend.get_commons_image.side_effect = slow_backend

    service = CachedPOIImageService(backend)

    results = await asyncio.gather(
        service.get_commons_image("example.jpg"),
        service.get_commons_image("example.jpg"),
    )

    assert len(results) == 2
    assert results[0].author == "Example Author"
    assert results[1].author == "Example Author"
    assert calls == 1


@pytest.mark.asyncio
async def test_failed_image_task_can_be_retried():
    backend = AsyncMock()

    backend.get_image.side_effect = [
        ExternalServiceError("Wikidata unavailable"),
        "coimbra.jpg",
    ]

    service = CachedPOIImageService(backend)

    with pytest.raises(ExternalServiceError):
        await service.get_image("Q2351947")

    assert ("wikidata", "Q2351947") not in service.in_flight

    result = await service.get_image("Q2351947")

    assert result == "coimbra.jpg"
    assert backend.get_image.await_count == 2


@pytest.mark.asyncio
async def test_cancelling_waiter_preserves_shared_task():
    backend = AsyncMock()

    started = asyncio.Event()
    release = asyncio.Event()

    async def slow_backend(wikidata_id):
        started.set()
        await release.wait()
        return "coimbra.jpg"

    backend.get_image.side_effect = slow_backend

    service = CachedPOIImageService(backend)

    first = asyncio.create_task(service.get_image("Q2351947"))

    await started.wait()

    second = asyncio.create_task(service.get_image("Q2351947"))

    await asyncio.sleep(0)

    first.cancel()

    with pytest.raises(asyncio.CancelledError):
        await first

    release.set()

    result = await second

    assert result == "coimbra.jpg"
    assert backend.get_image.await_count == 1
    assert ("wikidata", "Q2351947") not in service.in_flight
