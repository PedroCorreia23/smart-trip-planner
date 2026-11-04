from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.exceptions import ExternalServiceError
from app.services.poi_images import POIImageService


@pytest.fixture
def mock_wikidata():
    """Mock the Wikidata API without making real HTTP requests."""
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"entities": {}}

    client = AsyncMock()
    client.get.return_value = response

    context_manager = AsyncMock()
    context_manager.__aenter__.return_value = client

    with patch(
        "app.services.poi_images.httpx.AsyncClient",
        return_value=context_manager,
    ):
        yield client, response


@pytest.mark.asyncio
async def test_get_image_success(mock_wikidata):
    client, response = mock_wikidata

    response.json.return_value = {
        "entities": {
            "Q19675": {
                "claims": {
                    "P18": [
                        {
                            "mainsnak": {
                                "datavalue": {"value": "Cour Napoleon at night - Louvre.jpg"}
                            }
                        }
                    ]
                }
            }
        }
    }

    image = await POIImageService().get_image("Q19675")

    assert image == "Cour Napoleon at night - Louvre.jpg"
    client.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_image_no_p18(mock_wikidata):
    _, response = mock_wikidata

    response.json.return_value = {"entities": {"Q126281470": {"claims": {}}}}

    image = await POIImageService().get_image("Q126281470")

    assert image is None


@pytest.mark.asyncio
async def test_get_image_incomplete_p18(mock_wikidata):
    _, response = mock_wikidata

    response.json.return_value = {"entities": {"Q19675": {"claims": {"P18": [{"mainsnak": {}}]}}}}

    image = await POIImageService().get_image("Q19675")

    assert image is None


@pytest.mark.asyncio
async def test_get_image_http_error(mock_wikidata):
    _, response = mock_wikidata

    request = httpx.Request("GET", "https://www.wikidata.org/w/api.php")
    error_response = httpx.Response(503, request=request)

    response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Service Unavailable",
        request=request,
        response=error_response,
    )

    with pytest.raises(ExternalServiceError, match="HTTP error"):
        await POIImageService().get_image("Q19675")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error_type",
    [httpx.ConnectError, httpx.ReadTimeout],
)
async def test_get_image_request_error(mock_wikidata, error_type):
    client, _ = mock_wikidata

    request = httpx.Request("GET", "https://www.wikidata.org/w/api.php")

    client.get.side_effect = error_type(
        "Connection failed",
        request=request,
    )

    with pytest.raises(ExternalServiceError, match="unavailable"):
        await POIImageService().get_image("Q19675")
