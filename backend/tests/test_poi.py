from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.domain.schemas import POIInfo
from app.exceptions import ExternalServiceError
from app.services.poi import POIService


@pytest.fixture
def mock_geoapify():
    """Mock Geoapify requests without making real HTTP calls."""
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"features": []}

    client = AsyncMock()
    client.get.return_value = response

    context_manager = AsyncMock()
    context_manager.__aenter__.return_value = client

    with patch("app.services.poi.httpx.AsyncClient", return_value=context_manager):
        yield client, response


@pytest.mark.asyncio
async def test_get_pois_success(mock_geoapify):
    client, response = mock_geoapify

    response.json.return_value = {
        "features": [
            {
                "properties": {
                    "place_id": "museum-101",
                    "name": "Example Museum",
                    "categories": ["entertainment.museum"],
                    "lat": 48.8606,
                    "lon": 2.3376,
                }
            }
        ]
    }

    pois = await POIService().get_pois(48.8566, 2.3522)

    assert len(pois) == 1
    assert pois[0] == POIInfo(
        id="museum-101",
        name="Example Museum",
        category="entertainment.museum",
        lat=48.8606,
        lon=2.3376,
    )

    client.get.assert_awaited_once()

    params = client.get.await_args.kwargs["params"]

    assert params["categories"] == "entertainment.museum"
    assert params["filter"] == "circle:2.3522,48.8566,5000"
    assert params["limit"] == 20


@pytest.mark.asyncio
async def test_get_pois_custom_radius(mock_geoapify):
    client, response = mock_geoapify

    response.json.return_value = {"features": []}

    pois = await POIService().get_pois(
        48.8566,
        2.3522,
        radius=1000,
    )

    assert pois == []

    client.get.assert_awaited_once()

    params = client.get.await_args.kwargs["params"]

    assert params["filter"] == "circle:2.3522,48.8566,1000"


@pytest.mark.asyncio
async def test_get_pois_skips_unnamed_features(mock_geoapify):
    _, response = mock_geoapify

    response.json.return_value = {
        "features": [
            {
                "properties": {
                    "place_id": "museum-1",
                    "categories": ["entertainment.museum"],
                    "lat": 48.8,
                    "lon": 2.3,
                }
            },
            {
                "properties": {
                    "place_id": "museum-2",
                    "name": "Named Museum",
                    "categories": ["entertainment.museum"],
                    "lat": 48.9,
                    "lon": 2.4,
                }
            },
        ]
    }

    pois = await POIService().get_pois(48.8566, 2.3522)

    assert len(pois) == 1
    assert pois[0].id == "museum-2"
    assert pois[0].name == "Named Museum"


@pytest.mark.asyncio
async def test_get_pois_skips_missing_coordinates(mock_geoapify):
    _, response = mock_geoapify

    response.json.return_value = {
        "features": [
            {
                "properties": {
                    "place_id": "museum-3",
                    "name": "Museum Without Coordinates",
                    "categories": ["entertainment.museum"],
                }
            }
        ]
    }

    pois = await POIService().get_pois(48.8566, 2.3522)

    assert pois == []


@pytest.mark.asyncio
async def test_get_pois_empty_response(mock_geoapify):
    _, response = mock_geoapify

    response.json.return_value = {"features": []}

    assert await POIService().get_pois(48.8566, 2.3522) == []


@pytest.mark.asyncio
async def test_get_pois_http_error(mock_geoapify):
    _, response = mock_geoapify

    request = httpx.Request(
        "GET",
        "https://api.geoapify.com/v2/places",
    )

    error_response = httpx.Response(503, request=request)

    response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Service Unavailable",
        request=request,
        response=error_response,
    )

    with pytest.raises(ExternalServiceError, match="HTTP error"):
        await POIService().get_pois(48.8566, 2.3522)

@pytest.mark.asyncio
@pytest.mark.parametrize("error_type", [httpx.ConnectError, httpx.ReadTimeout])
async def test_get_pois_request_error(mock_geoapify, error_type):
    client, _ = mock_geoapify

    request = httpx.Request(
        "GET",
        "https://api.geoapify.com/v2/places",
    )

    client.get.side_effect = error_type(
        "Connection failed",
        request=request,
    )

    with pytest.raises(ExternalServiceError, match="unavailable"):
        await POIService().get_pois(48.8566, 2.3522)
