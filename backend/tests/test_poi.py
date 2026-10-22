from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.domain.schemas import POIInfo
from app.exceptions import ExternalServiceError
from app.services.poi import POIService


@pytest.fixture
def mock_overpass():
    """Mock the Overpass request without making an HTTP call."""
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"elements": []}

    client = AsyncMock()
    client.post.return_value = response

    context_manager = AsyncMock()
    context_manager.__aenter__.return_value = client

    with patch("app.services.poi.httpx.AsyncClient", return_value=context_manager):
        yield client, response


@pytest.mark.asyncio
async def test_get_pois_node(mock_overpass):
    client, response = mock_overpass
    response.json.return_value = {
        "elements": [
            {
                "type": "node",
                "id": 101,
                "lat": 48.8606,
                "lon": 2.3376,
                "tags": {"name": "Example Museum", "tourism": "museum"},
            }
        ]
    }

    pois = await POIService().get_pois(48.8566, 2.3522)

    assert len(pois) == 1
    assert pois[0] == POIInfo(
        id=101, name="Example Museum", category="museum", lat=48.8606, lon=2.3376
    )
    assert client.post.await_count == 1
    assert "around:5000,48.8566,2.3522" in client.post.await_args.kwargs["data"]["data"]


@pytest.mark.asyncio
async def test_get_pois_way_with_center(mock_overpass):
    _, response = mock_overpass
    response.json.return_value = {
        "elements": [
            {
                "type": "way",
                "id": 202,
                "center": {"lat": 48.861, "lon": 2.336},
                "tags": {"name": "Museum Building", "tourism": "museum"},
            }
        ]
    }

    pois = await POIService().get_pois(48.8566, 2.3522, radius=1000)

    assert len(pois) == 1
    assert pois[0].lat == 48.861
    assert pois[0].lon == 2.336
    assert pois[0].name == "Museum Building"


@pytest.mark.asyncio
async def test_get_pois_skips_unnamed_elements(mock_overpass):
    _, response = mock_overpass
    response.json.return_value = {
        "elements": [
            {"type": "node", "id": 1, "lat": 48.8, "lon": 2.3, "tags": {"tourism": "museum"}},
            {
                "type": "node",
                "id": 2,
                "lat": 48.9,
                "lon": 2.4,
                "tags": {"name": "Named Museum", "tourism": "museum"},
            },
        ]
    }

    pois = await POIService().get_pois(48.8566, 2.3522)

    assert len(pois) == 1
    assert pois[0].id == 2


@pytest.mark.asyncio
async def test_get_pois_skips_way_without_center(mock_overpass):
    _, response = mock_overpass
    response.json.return_value = {
        "elements": [{"type": "way", "id": 3, "tags": {"name": "No Center", "tourism": "museum"}}]
    }

    assert await POIService().get_pois(48.8566, 2.3522) == []


@pytest.mark.asyncio
async def test_get_pois_empty_response(mock_overpass):
    _, response = mock_overpass
    response.json.return_value = {"elements": []}

    assert await POIService().get_pois(48.8566, 2.3522) == []


@pytest.mark.asyncio
async def test_get_pois_http_error(mock_overpass):
    _, response = mock_overpass
    request = httpx.Request("POST", "https://overpass-api.de/api/interpreter")
    error_response = httpx.Response(503, request=request)
    response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Service Unavailable", request=request, response=error_response
    )

    with pytest.raises(ExternalServiceError, match="HTTP error"):
        await POIService().get_pois(48.8566, 2.3522)


@pytest.mark.asyncio
@pytest.mark.parametrize("error_type", [httpx.ConnectError, httpx.ReadTimeout])
async def test_get_pois_request_error(mock_overpass, error_type):
    client, _ = mock_overpass
    request = httpx.Request("POST", "https://overpass-api.de/api/interpreter")
    client.post.side_effect = error_type("Connection failed", request=request)

    with pytest.raises(ExternalServiceError, match="unavailable"):
        await POIService().get_pois(48.8566, 2.3522)
