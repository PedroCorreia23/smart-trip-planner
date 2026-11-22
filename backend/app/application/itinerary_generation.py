from app.domain.distance import haversine_distance
from app.domain.schemas import POIInfo


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


def calculate_daily_capacity(num_pois: int, num_days: int) -> list[int]:
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

    # Continuar aqui