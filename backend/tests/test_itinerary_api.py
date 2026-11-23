import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_generate_itinerary_success():
    payload = {
        "start_date": "2026-12-10",
        "end_date": "2026-12-11",
        "pois": [
            {
                "id": "1",
                "name": "Louvre",
                "category": "museum",
                "lat": 48.8606,
                "lon": 2.3376,
            },
            {
                "id": "2",
                "name": "Eiffel Tower",
                "category": "monument",
                "lat": 48.8584,
                "lon": 2.2945,
            },
            {
                "id": "3",
                "name": "Musée d'Orsay",
                "category": "museum",
                "lat": 48.8600,
                "lon": 2.3266,
            },
        ],
    }

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/itineraries/generate",
            json=payload,
        )

    assert response.status_code == 200

    data = response.json()

    assert len(data["days"]) == 2
    assert data["days"][0]["day"] == "2026-12-10"
    assert data["days"][1]["day"] == "2026-12-11"

    assert [len(day["pois"]) for day in data["days"]] == [2, 1]

    assert [poi["id"] for poi in data["days"][0]["pois"]] == [
        "1",
        "3",
    ]
    assert data["days"][1]["pois"][0]["id"] == "2"


@pytest.mark.asyncio
async def test_generate_itinerary_invalid_dates():
    payload = {
        "start_date": "2026-12-15",
        "end_date": "2026-12-10",
        "pois": [],
    }

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/itineraries/generate",
            json=payload,
        )

    assert response.status_code == 422
