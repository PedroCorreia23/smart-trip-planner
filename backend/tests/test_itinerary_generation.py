from app.application.itinerary_generation import find_nearest_poi
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
    with pytest.raises(ValueError, match="Number of days must be positive"):
        calculate_daily_capacity(5, 0)

def test_daily_capacity_even_distribution():
    result = calculate_daily_capacity(6, 3)

    assert result == [2, 2, 2]