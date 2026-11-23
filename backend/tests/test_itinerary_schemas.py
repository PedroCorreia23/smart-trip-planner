from datetime import date

import pytest
from pydantic import ValidationError

from app.domain.schemas import (
    ItineraryDay,
    ItineraryRequest,
    ItineraryResponse,
)


def test_itinerary_request_valid_dates():
    request = ItineraryRequest(
        start_date=date(2026, 12, 10),
        end_date=date(2026, 12, 12),
        pois=[],
    )

    assert request.start_date == date(2026, 12, 10)
    assert request.end_date == date(2026, 12, 12)
    assert request.pois == []


def test_itinerary_request_invalid_dates():
    with pytest.raises(
        ValidationError,
        match="End date must be on or after start date",
    ):
        ItineraryRequest(
            start_date=date(2026, 12, 15),
            end_date=date(2026, 12, 10),
            pois=[],
        )


def test_itinerary_request_same_day():
    request = ItineraryRequest(
        start_date=date(2026, 12, 10),
        end_date=date(2026, 12, 10),
        pois=[],
    )

    assert request.start_date == request.end_date


def test_itinerary_day():
    day = ItineraryDay(
        day=date(2026, 12, 10),
        pois=[],
    )

    assert day.day == date(2026, 12, 10)
    assert day.pois == []


def test_itinerary_response():
    response = ItineraryResponse(
        days=[
            ItineraryDay(
                day=date(2026, 12, 10),
                pois=[],
            ),
            ItineraryDay(
                day=date(2026, 12, 11),
                pois=[],
            ),
        ]
    )

    assert len(response.days) == 2
    assert response.days[0].day == date(2026, 12, 10)
    assert response.days[1].day == date(2026, 12, 11)
