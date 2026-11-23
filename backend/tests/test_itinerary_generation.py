import pytest

from app.application.itinerary_generation import (
    calculate_daily_capacity,
    find_nearest_poi,
    group_pois_by_day,
)
from app.domain.schemas import POIInfo


def test_find_nearest_poi():
    louvre = POIInfo(
        id="1",
        name="Louvre",
        category="museum",
        lat=48.8606,
        lon=2.3376,
    )

    eiffel = POIInfo(
        id="2",
        name="Eiffel Tower",
        category="monument",
        lat=48.8584,
        lon=2.2945,
    )

    orsay = POIInfo(
        id="3",
        name="Musée d'Orsay",
        category="museum",
        lat=48.8600,
        lon=2.3266,
    )

    nearest = find_nearest_poi(louvre, [eiffel, orsay])

    assert nearest == orsay


def test_find_nearest_poi_empty_list():
    louvre = POIInfo(
        id="1",
        name="Louvre",
        category="museum",
        lat=48.8606,
        lon=2.3376,
    )

    nearest = find_nearest_poi(louvre, [])

    assert nearest is None


def test_find_nearest_poi_single_candidate():
    louvre = POIInfo(
        id="1",
        name="Louvre",
        category="museum",
        lat=48.8606,
        lon=2.3376,
    )

    eiffel = POIInfo(
        id="2",
        name="Eiffel Tower",
        category="monument",
        lat=48.8584,
        lon=2.2945,
    )

    nearest = find_nearest_poi(louvre, [eiffel])

    assert nearest == eiffel


def test_daily_capacity_invalid_days():
    with pytest.raises(
        ValueError,
        match="Number of days must be positive",
    ):
        calculate_daily_capacity(5, 0)


def test_daily_capacity_even_distribution():
    result = calculate_daily_capacity(6, 3)

    assert result == [2, 2, 2]


def test_daily_capacity_with_remainder():
    result = calculate_daily_capacity(7, 3)

    assert result == [3, 2, 2]


def test_daily_capacity_more_days_than_pois():
    result = calculate_daily_capacity(2, 5)

    assert result == [1, 1, 0, 0, 0]


def test_daily_capacity_no_pois():
    result = calculate_daily_capacity(0, 3)

    assert result == [0, 0, 0]


def test_group_pois_by_day_distribution():
    pois = [
        POIInfo(
            id=str(i),
            name=f"POI {i}",
            category="museum",
            lat=48.85 + i * 0.001,
            lon=2.35,
        )
        for i in range(5)
    ]

    itinerary = group_pois_by_day(pois, 2)

    assert len(itinerary) == 2
    assert len(itinerary[0]) == 3
    assert len(itinerary[1]) == 2


def test_group_pois_by_day_no_duplicates():
    pois = [
        POIInfo(
            id=str(i),
            name=f"POI {i}",
            category="museum",
            lat=48.85 + i * 0.001,
            lon=2.35,
        )
        for i in range(5)
    ]

    itinerary = group_pois_by_day(pois, 2)

    all_ids = [poi.id for day in itinerary for poi in day]

    assert len(all_ids) == len(pois)
    assert len(set(all_ids)) == len(pois)
    assert set(all_ids) == {poi.id for poi in pois}


def test_group_pois_by_day_more_days_than_pois():
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

    itinerary = group_pois_by_day(pois, 5)

    assert len(itinerary) == 5
    assert [len(day) for day in itinerary] == [1, 1, 0, 0, 0]


def test_group_pois_by_day_empty_list():
    itinerary = group_pois_by_day([], 3)

    assert itinerary == [[], [], []]


def test_group_pois_by_day_nearest_first():
    louvre = POIInfo(
        id="1",
        name="Louvre",
        category="museum",
        lat=48.8606,
        lon=2.3376,
    )

    eiffel = POIInfo(
        id="2",
        name="Eiffel Tower",
        category="monument",
        lat=48.8584,
        lon=2.2945,
    )

    orsay = POIInfo(
        id="3",
        name="Musée d'Orsay",
        category="museum",
        lat=48.8600,
        lon=2.3266,
    )

    itinerary = group_pois_by_day(
        [louvre, eiffel, orsay],
        1,
    )

    assert len(itinerary) == 1
    assert itinerary[0][0] == louvre
    assert itinerary[0][1] == orsay
    assert itinerary[0][2] == eiffel
