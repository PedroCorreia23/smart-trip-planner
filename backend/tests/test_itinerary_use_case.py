from datetime import date

import pytest

from app.application.itinerary_generation import ItineraryGenerationUseCase
from app.domain.schemas import (
    ItineraryRequest,
    ItineraryResponse,
    POIInfo,
)


@pytest.fixture
def sample_pois():
    return [
        POIInfo(
            id=str(i),
            name=f"POI {i}",
            category="museum",
            lat=48.85 + i * 0.001,
            lon=2.35,
        )
        for i in range(5)
    ]


def test_itinerary_use_case_distribution(sample_pois):
    request = ItineraryRequest(
        start_date=date(2026, 12, 10),
        end_date=date(2026, 12, 11),
        pois=sample_pois,
    )

    use_case = ItineraryGenerationUseCase()
    result = use_case.execute(request)

    assert isinstance(result, ItineraryResponse)
    assert len(result.days) == 2
    assert [len(day.pois) for day in result.days] == [3, 2]


def test_itinerary_use_case_correct_dates(sample_pois):
    request = ItineraryRequest(
        start_date=date(2026, 12, 10),
        end_date=date(2026, 12, 12),
        pois=sample_pois,
    )

    result = ItineraryGenerationUseCase().execute(request)

    assert [day.day for day in result.days] == [
        date(2026, 12, 10),
        date(2026, 12, 11),
        date(2026, 12, 12),
    ]


def test_itinerary_use_case_single_day(sample_pois):
    request = ItineraryRequest(
        start_date=date(2026, 12, 10),
        end_date=date(2026, 12, 10),
        pois=sample_pois,
    )

    result = ItineraryGenerationUseCase().execute(request)

    assert len(result.days) == 1
    assert result.days[0].day == date(2026, 12, 10)
    assert len(result.days[0].pois) == 5


def test_itinerary_use_case_no_pois():
    request = ItineraryRequest(
        start_date=date(2026, 12, 10),
        end_date=date(2026, 12, 12),
        pois=[],
    )

    result = ItineraryGenerationUseCase().execute(request)

    assert len(result.days) == 3
    assert all(day.pois == [] for day in result.days)


def test_itinerary_use_case_more_days_than_pois():
    pois = [
        POIInfo(
            id=str(i),
            name=f"POI {i}",
            category="museum",
            lat=48.85 + i * 0.001,
            lon=2.35,
        )
        for i in range(2)
    ]

    request = ItineraryRequest(
        start_date=date(2026, 12, 10),
        end_date=date(2026, 12, 14),
        pois=pois,
    )

    result = ItineraryGenerationUseCase().execute(request)

    assert len(result.days) == 5
    assert [len(day.pois) for day in result.days] == [1, 1, 0, 0, 0]


def test_itinerary_use_case_preserves_all_pois(sample_pois):
    request = ItineraryRequest(
        start_date=date(2026, 12, 10),
        end_date=date(2026, 12, 12),
        pois=sample_pois,
    )

    result = ItineraryGenerationUseCase().execute(request)

    result_ids = [poi.id for day in result.days for poi in day.pois]

    original_ids = [poi.id for poi in sample_pois]

    assert len(result_ids) == len(original_ids)
    assert set(result_ids) == set(original_ids)
