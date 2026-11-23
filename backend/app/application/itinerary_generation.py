from datetime import timedelta

from app.domain.distance import haversine_distance
from app.domain.schemas import (
    ItineraryDay,
    ItineraryRequest,
    ItineraryResponse,
    POIInfo,
)


def find_nearest_poi(
    current_poi: POIInfo,
    remaining_pois: list[POIInfo],
) -> POIInfo | None:
    min_distance = float("inf")
    nearest_poi = None

    for poi in remaining_pois:
        distance = haversine_distance(
            current_poi.lat,
            current_poi.lon,
            poi.lat,
            poi.lon,
        )

        if distance < min_distance:
            min_distance = distance
            nearest_poi = poi

    return nearest_poi


def calculate_daily_capacity(
    num_pois: int,
    num_days: int,
) -> list[int]:
    if num_days <= 0:
        raise ValueError("Number of days must be positive.")

    base, remainder = divmod(num_pois, num_days)

    return [base + (1 if day < remainder else 0) for day in range(num_days)]


def group_pois_by_day(
    pois: list[POIInfo],
    num_days: int,
) -> list[list[POIInfo]]:
    capacities = calculate_daily_capacity(len(pois), num_days)

    remaining_pois = pois.copy()
    itinerary = []

    for capacity in capacities:
        day_pois = []

        if capacity > 0:
            current_poi = remaining_pois.pop(0)
            day_pois.append(current_poi)

            for _ in range(capacity - 1):
                nearest_poi = find_nearest_poi(
                    current_poi,
                    remaining_pois,
                )

                day_pois.append(nearest_poi)
                remaining_pois.remove(nearest_poi)
                current_poi = nearest_poi

        itinerary.append(day_pois)

    return itinerary


class ItineraryGenerationUseCase:
    def execute(self, request: ItineraryRequest) -> ItineraryResponse:
        num_days = (request.end_date - request.start_date).days + 1

        grouped_pois = group_pois_by_day(
            request.pois,
            num_days,
        )

        days = []

        for index, day_pois in enumerate(grouped_pois):
            current_date = request.start_date + timedelta(days=index)

            itinerary_day = ItineraryDay(
                day=current_date,
                pois=day_pois,
            )

            days.append(itinerary_day)

        return ItineraryResponse(days=days)
