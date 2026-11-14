from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.application.poi_search import POISearchUseCase
from app.dependencies import get_poi_search_use_case
from app.domain.schemas import POIInfo
from app.exceptions import ExternalServiceError
from app.main import app
from app.services.poi_fallback import FallbackPOIService


def test_endpoint_uses_geoapify_when_wikidata_fails():
    primary = AsyncMock()
    fallback = AsyncMock()
    image_service = AsyncMock()

    primary.get_pois.side_effect = ExternalServiceError("Wikidata unavailable")

    fallback.get_pois.return_value = [
        POIInfo(
            id="geoapify-123",
            name="Mosteiro de Santa Cruz",
            category="monument",
            lat=40.210945,
            lon=-8.428761,
        )
    ]

    fallback.get_wikidata_id.return_value = None

    poi_service = FallbackPOIService(
        primary=primary,
        fallback=fallback,
        timeout=7.0,
    )

    use_case = POISearchUseCase(
        poi_service=poi_service,
        poi_image_service=image_service,
    )

    app.dependency_overrides[get_poi_search_use_case] = lambda: use_case

    try:
        with TestClient(app) as client:
            response = client.get(
                "/pois",
                params={
                    "lat": 40.2033,
                    "lon": -8.4103,
                    "radius": 5000,
                    "category": "monument",
                },
            )

        assert response.status_code == 200

        pois = response.json()

        assert len(pois) == 1
        assert pois[0]["id"] == "geoapify-123"
        assert pois[0]["name"] == "Mosteiro de Santa Cruz"

        primary.get_pois.assert_awaited_once()
        fallback.get_pois.assert_awaited_once()

    finally:
        app.dependency_overrides.pop(
            get_poi_search_use_case,
            None,
        )


def test_endpoint_uses_geoapify_when_wikidata_empty():
    primary = AsyncMock()
    fallback = AsyncMock()
    image_service = AsyncMock()

    primary.get_pois.return_value = []

    fallback.get_pois.return_value = [
        POIInfo(
            id="geoapify-456",
            name="Sé Velha de Coimbra",
            category="monument",
            lat=40.208561,
            lon=-8.426922,
        )
    ]

    fallback.get_wikidata_id.return_value = None

    poi_service = FallbackPOIService(
        primary=primary,
        fallback=fallback,
        timeout=7.0,
    )

    use_case = POISearchUseCase(
        poi_service=poi_service,
        poi_image_service=image_service,
    )

    app.dependency_overrides[get_poi_search_use_case] = lambda: use_case

    try:
        with TestClient(app) as client:
            response = client.get(
                "/pois",
                params={
                    "lat": 40.2033,
                    "lon": -8.4103,
                    "radius": 5000,
                    "category": "monument",
                },
            )

        assert response.status_code == 200

        pois = response.json()

        assert len(pois) == 1
        assert pois[0]["id"] == "geoapify-456"
        assert pois[0]["name"] == "Sé Velha de Coimbra"

        primary.get_pois.assert_awaited_once()
        fallback.get_pois.assert_awaited_once()

    finally:
        app.dependency_overrides.pop(
            get_poi_search_use_case,
            None,
        )
