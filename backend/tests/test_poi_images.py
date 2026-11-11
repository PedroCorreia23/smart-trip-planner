from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from app.domain.schemas import POIImageInfo
from app.exceptions import ExternalServiceError
from app.services.poi_images import POIImageService, clean_html_text


@pytest.fixture
def mock_wikidata():
    """Mock the Wikidata API without making real HTTP requests."""
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"entities": {}}

    client = AsyncMock(spec=httpx.AsyncClient)
    client.get.return_value = response

    return client, response


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

    service = POIImageService(client)
    image = await service.get_image("Q19675")

    assert image == "Cour Napoleon at night - Louvre.jpg"
    client.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_image_no_p18(mock_wikidata):
    client, response = mock_wikidata

    response.json.return_value = {"entities": {"Q126281470": {"claims": {}}}}

    service = POIImageService(client)
    image = await service.get_image("Q126281470")

    assert image is None


@pytest.mark.asyncio
async def test_get_image_incomplete_p18(mock_wikidata):
    client, response = mock_wikidata

    response.json.return_value = {"entities": {"Q19675": {"claims": {"P18": [{"mainsnak": {}}]}}}}

    service = POIImageService(client)
    image = await service.get_image("Q19675")

    assert image is None


@pytest.mark.asyncio
async def test_get_image_http_error(mock_wikidata):
    client, response = mock_wikidata

    request = httpx.Request("GET", "https://www.wikidata.org/w/api.php")
    error_response = httpx.Response(503, request=request)

    response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Service Unavailable",
        request=request,
        response=error_response,
    )

    with pytest.raises(ExternalServiceError, match="HTTP error"):
        await POIImageService(client).get_image("Q19675")


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
        await POIImageService(client).get_image("Q19675")


@pytest.fixture
def mock_commons():
    """Mock the Wikimedia Commons API without making real HTTP requests."""
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"query": {"pages": {}}}

    client = AsyncMock(spec=httpx.AsyncClient)
    client.get.return_value = response

    return client, response


@pytest.mark.asyncio
async def test_get_commons_image_success(mock_commons):
    client, response = mock_commons

    response.json.return_value = {
        "query": {
            "pages": {
                "2768109": {
                    "imageinfo": [
                        {
                            "url": "https://example.com/louvre.jpg",
                            "thumburl": "https://example.com/louvre-small.jpg",
                            "descriptionurl": "https://commons.wikimedia.org/wiki/File:Louvre.jpg",
                            "extmetadata": {
                                "Artist": {"value": "Example Photographer"},
                                "LicenseShortName": {"value": "CC BY 2.5"},
                            },
                        }
                    ]
                }
            }
        }
    }

    service = POIImageService(client)
    image = await service.get_commons_image("Louvre.jpg")

    assert isinstance(image, POIImageInfo)
    assert image.url == "https://example.com/louvre.jpg"
    assert image.thumbnail_url == "https://example.com/louvre-small.jpg"
    assert image.author == "Example Photographer"
    assert image.license == "CC BY 2.5"
    assert image.description_url == "https://commons.wikimedia.org/wiki/File:Louvre.jpg"

    client.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_commons_image_not_found(mock_commons):
    client, response = mock_commons

    response.json.return_value = {
        "query": {
            "pages": {
                "-1": {
                    "title": "File:Unknown.jpg",
                    "missing": "",
                }
            }
        }
    }

    image = await POIImageService(client).get_commons_image("Unknown.jpg")

    assert image is None


@pytest.mark.asyncio
async def test_get_commons_image_missing_url(mock_commons):
    client, response = mock_commons

    response.json.return_value = {
        "query": {
            "pages": {
                "123": {
                    "imageinfo": [
                        {
                            "thumburl": "https://example.com/small.jpg",
                            "extmetadata": {},
                        }
                    ]
                }
            }
        }
    }

    image = await POIImageService(client).get_commons_image("Example.jpg")

    assert image is None


@pytest.mark.asyncio
async def test_get_commons_image_missing_metadata(mock_commons):
    client, response = mock_commons

    response.json.return_value = {
        "query": {
            "pages": {
                "123": {
                    "imageinfo": [
                        {
                            "url": "https://example.com/image.jpg",
                        }
                    ]
                }
            }
        }
    }

    image = await POIImageService(client).get_commons_image("Example.jpg")

    assert isinstance(image, POIImageInfo)
    assert image.url == "https://example.com/image.jpg"
    assert image.thumbnail_url is None
    assert image.author is None
    assert image.license is None
    assert image.description_url is None


@pytest.mark.asyncio
async def test_get_commons_image_http_error(mock_commons):
    client, response = mock_commons

    request = httpx.Request(
        "GET",
        "https://commons.wikimedia.org/w/api.php",
    )
    error_response = httpx.Response(503, request=request)

    response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Service Unavailable",
        request=request,
        response=error_response,
    )

    with pytest.raises(ExternalServiceError, match="HTTP error"):
        await POIImageService(client).get_commons_image("Louvre.jpg")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error_type",
    [httpx.ConnectError, httpx.ReadTimeout],
)
async def test_get_commons_image_request_error(mock_commons, error_type):
    client, _ = mock_commons

    request = httpx.Request(
        "GET",
        "https://commons.wikimedia.org/w/api.php",
    )

    client.get.side_effect = error_type(
        "Connection failed",
        request=request,
    )

    with pytest.raises(ExternalServiceError, match="unavailable"):
        await POIImageService(client).get_commons_image("Louvre.jpg")


def test_clean_html_text():
    html = '<a href="/wiki/User:Example">Example Author</a>'

    result = clean_html_text(html)

    assert result == "Example Author"
