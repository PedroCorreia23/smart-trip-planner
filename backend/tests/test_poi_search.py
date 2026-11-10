from unittest.mock import AsyncMock

import pytest

from app.application.poi_search import POISearchUseCase
from app.domain.schemas import POIImageInfo, POIInfo
from app.exceptions import ExternalServiceError


@pytest.fixture
def mock_services():
    poi_service = AsyncMock()
    poi_image_service = AsyncMock()

    use_case = POISearchUseCase(
        poi_service=poi_service,
        poi_image_service=poi_image_service,
    )

    poi = POIInfo(
        id="example-place-id",
        name="Louvre Museum",
        category="entertainment.museum",
        lat=48.8606,
        lon=2.3376,
    )

    return use_case, poi_service, poi_image_service, poi


@pytest.mark.asyncio
async def test_enrich_poi_success(mock_services):
    use_case, poi_service, poi_image_service, poi = mock_services

    poi_service.get_wikidata_id.return_value = "Q19675"
    poi_image_service.get_image.return_value = "Louvre.jpg"
    poi_image_service.get_commons_image.return_value = POIImageInfo(
        url="https://commons.wikimedia.org/original.jpg",
        thumbnail_url="https://commons.wikimedia.org/thumb.jpg",
        author="Example Author",
        license="CC BY 4.0",
        description_url="https://commons.wikimedia.org/wiki/File:Louvre.jpg",
    )

    result = await use_case.enrich_poi(poi)

    # Verificar a imagem e os metadados
    assert result.image_url == "https://commons.wikimedia.org/thumb.jpg"
    assert result.image_author == "Example Author"
    assert result.image_license == "CC BY 4.0"
    assert result.image_source_url == "https://commons.wikimedia.org/wiki/File:Louvre.jpg"

    # Verificar que o objeto original não foi modificado
    assert poi.image_url is None
    assert poi.image_author is None
    assert poi.image_license is None
    assert poi.image_source_url is None

    # Verificar as chamadas aos serviços
    poi_service.get_wikidata_id.assert_awaited_once_with(poi.id)
    poi_image_service.get_image.assert_awaited_once_with("Q19675")
    poi_image_service.get_commons_image.assert_awaited_once_with("Louvre.jpg")


@pytest.mark.asyncio
async def test_enrich_poi_no_wikidata(mock_services):
    use_case, poi_service, poi_image_service, poi = mock_services

    poi_service.get_wikidata_id.return_value = None

    result = await use_case.enrich_poi(poi)

    assert result == poi
    poi_image_service.get_image.assert_not_awaited()
    poi_image_service.get_commons_image.assert_not_awaited()


@pytest.mark.asyncio
async def test_enrich_poi_no_p18(mock_services):
    use_case, poi_service, poi_image_service, poi = mock_services

    poi_service.get_wikidata_id.return_value = "Q19675"
    poi_image_service.get_image.return_value = None

    result = await use_case.enrich_poi(poi)

    assert result == poi
    poi_image_service.get_commons_image.assert_not_awaited()


@pytest.mark.asyncio
async def test_enrich_poi_no_commons_image(mock_services):
    use_case, poi_service, poi_image_service, poi = mock_services

    poi_service.get_wikidata_id.return_value = "Q19675"
    poi_image_service.get_image.return_value = "Louvre.jpg"
    poi_image_service.get_commons_image.return_value = None

    result = await use_case.enrich_poi(poi)

    assert result == poi


@pytest.mark.asyncio
async def test_enrich_poi_external_service_error(mock_services):
    use_case, poi_service, poi_image_service, poi = mock_services

    poi_service.get_wikidata_id.side_effect = ExternalServiceError("Geoapify unavailable.")

    result = await use_case.enrich_poi(poi)

    assert result == poi
    poi_image_service.get_image.assert_not_awaited()
    poi_image_service.get_commons_image.assert_not_awaited()


@pytest.mark.asyncio
async def test_enrich_poi_fallback_to_original_url(mock_services):
    use_case, poi_service, poi_image_service, poi = mock_services

    poi_service.get_wikidata_id.return_value = "Q19675"
    poi_image_service.get_image.return_value = "Louvre.jpg"
    poi_image_service.get_commons_image.return_value = POIImageInfo(
        url="https://example.com/louvre.jpg",
        thumbnail_url=None,
    )

    result = await use_case.enrich_poi(poi)

    assert result.image_url == "https://example.com/louvre.jpg"
