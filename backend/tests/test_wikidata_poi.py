import httpx
import pytest

from app.exceptions import ExternalServiceError
from app.services.wikidata_poi import (
    WikidataPOIService,
    parse_coordinates,
)


def test_parse_coordinates():
    result = parse_coordinates("Point(-8.4265 40.2071)")

    assert result == (40.2071, -8.4265)


def test_parse_invalid_coordinates():
    assert parse_coordinates("invalid") is None
    assert parse_coordinates("Point(200 40)") is None


@pytest.mark.asyncio
async def test_wikidata_poi_service_returns_pois():
    def handler(request):
        if request.url.path == "/sparql":
            return httpx.Response(
                200,
                json={
                    "results": {
                        "bindings": [
                            {
                                "place": {"value": ("http://www.wikidata.org/entity/Q1773229")},
                                "location": {"value": "Point(-8.4265 40.2071)"},
                                "sitelinks": {"value": "12"},
                            }
                        ]
                    }
                },
            )

        return httpx.Response(
            200,
            json={"entities": {"Q1773229": {"labels": {"pt": {"value": "Biblioteca Joanina"}}}}},
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as client:
        service = WikidataPOIService(client)

        pois = await service.get_pois(
            lat=40.2033,
            lon=-8.4103,
            radius=5000,
            category="attraction",
        )

    assert len(pois) == 1
    assert pois[0].name == "Biblioteca Joanina"
    assert pois[0].wikidata_id == "Q1773229"
    assert pois[0].category == "attraction"
    assert pois[0].lat == 40.2071
    assert pois[0].lon == -8.4265


@pytest.mark.asyncio
async def test_wikidata_poi_service_empty_results():
    def handler(request):
        return httpx.Response(
            200,
            json={"results": {"bindings": []}},
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as client:
        service = WikidataPOIService(client)

        pois = await service.get_pois(
            lat=40.2033,
            lon=-8.4103,
            category="museum",
        )

    assert pois == []


@pytest.mark.asyncio
async def test_wikidata_poi_service_skips_missing_names():
    def handler(request):
        if request.url.path == "/sparql":
            return httpx.Response(
                200,
                json={
                    "results": {
                        "bindings": [
                            {
                                "place": {"value": ("http://www.wikidata.org/entity/Q1580762")},
                                "location": {"value": "Point(-8.4333 40.2125)"},
                            }
                        ]
                    }
                },
            )

        return httpx.Response(
            200,
            json={"entities": {"Q1580762": {"labels": {}}}},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        service = WikidataPOIService(client)

        pois = await service.get_pois(
            lat=40.2033,
            lon=-8.4103,
            category="monument",
        )

    assert pois == []


@pytest.mark.asyncio
async def test_wikidata_poi_service_handles_http_error():
    def handler(request):
        return httpx.Response(503)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        service = WikidataPOIService(client)

        with pytest.raises(ExternalServiceError):
            await service.get_pois(
                lat=40.2033,
                lon=-8.4103,
                category="museum",
            )


@pytest.mark.asyncio
async def test_wikidata_poi_service_skips_invalid_coordinates():
    def handler(request):
        return httpx.Response(
            200,
            json={
                "results": {
                    "bindings": [
                        {
                            "place": {"value": ("http://www.wikidata.org/entity/Q1773229")},
                            "location": {"value": "Point(200 40)"},
                        }
                    ]
                }
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        service = WikidataPOIService(client)

        pois = await service.get_pois(
            lat=40.2033,
            lon=-8.4103,
            category="attraction",
        )

    assert pois == []


@pytest.mark.asyncio
async def test_wikidata_poi_service_removes_duplicates():
    calls = {"names": 0}

    def handler(request):
        if request.url.path == "/sparql":
            binding = {
                "place": {"value": ("http://www.wikidata.org/entity/Q19675")},
                "location": {"value": "Point(2.3358 48.8606)"},
            }

            return httpx.Response(
                200,
                json={"results": {"bindings": [binding, binding]}},
            )

        calls["names"] += 1

        return httpx.Response(
            200,
            json={"entities": {"Q19675": {"labels": {"en": {"value": "Louvre Museum"}}}}},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        service = WikidataPOIService(client)

        pois = await service.get_pois(
            lat=48.8566,
            lon=2.3522,
            category="museum",
        )

    assert len(pois) == 1
    assert pois[0].wikidata_id == "Q19675"
    assert calls["names"] == 1


@pytest.mark.asyncio
async def test_wikidata_poi_service_handles_invalid_json():
    def handler(request):
        return httpx.Response(
            200,
            text="Invalid JSON",
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        service = WikidataPOIService(client)

        with pytest.raises(ExternalServiceError):
            await service.get_pois(
                lat=48.8566,
                lon=2.3522,
                category="museum",
            )


@pytest.mark.asyncio
async def test_wikidata_poi_service_preserves_ranking():
    def handler(request):
        if request.url.path == "/sparql":
            return httpx.Response(
                200,
                json={
                    "results": {
                        "bindings": [
                            {
                                "place": {"value": ("http://www.wikidata.org/entity/Q19675")},
                                "location": {"value": "Point(2.3358 48.8606)"},
                            },
                            {
                                "place": {"value": ("http://www.wikidata.org/entity/Q23402")},
                                "location": {"value": "Point(2.3266 48.86)"},
                            },
                        ]
                    }
                },
            )

        return httpx.Response(
            200,
            json={
                "entities": {
                    "Q23402": {"labels": {"en": {"value": "Musée d'Orsay"}}},
                    "Q19675": {"labels": {"en": {"value": "Louvre Museum"}}},
                }
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        service = WikidataPOIService(client)

        pois = await service.get_pois(
            lat=48.8566,
            lon=2.3522,
            category="museum",
        )

    assert [poi.wikidata_id for poi in pois] == [
        "Q19675",
        "Q23402",
    ]
