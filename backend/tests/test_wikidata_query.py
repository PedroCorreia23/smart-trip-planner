import pytest

from app.services.wikidata_query import (
    build_poi_query,
)


def test_build_poi_query_includes_coordinates():
    query = build_poi_query(
        lat=48.8566,
        lon=2.3522,
        radius=5000,
        category="museum",
    )

    assert "Point(2.3522 48.8566)" in query


def test_build_poi_query_converts_radius_to_km():
    query = build_poi_query(
        lat=48.8566,
        lon=2.3522,
        radius=5000,
        category="museum",
    )

    assert 'wikibase:radius "5.0"' in query


def test_build_poi_query_uses_category_types():
    query = build_poi_query(
        lat=40.2033,
        lon=-8.4103,
        radius=5000,
        category="monument",
    )

    assert "wd:Q2977" in query
    assert "wd:Q44613" in query


def test_build_poi_query_returns_coordinates():
    query = build_poi_query(
        lat=48.8566,
        lon=2.3522,
        radius=5000,
        category="park",
    )

    assert "?location" in query


def test_build_poi_query_rejects_invalid_category():
    with pytest.raises(ValueError):
        build_poi_query(
            lat=48.8566,
            lon=2.3522,
            radius=5000,
            category="restaurant",
        )


@pytest.mark.parametrize(
    ("lat", "lon", "radius"),
    [
        (91, 2.3522, 5000),
        (48.8566, 181, 5000),
        (48.8566, 2.3522, 0),
    ],
)
def test_build_poi_query_rejects_invalid_location(lat, lon, radius):
    with pytest.raises(ValueError):
        build_poi_query(
            lat=lat,
            lon=lon,
            radius=radius,
            category="museum",
        )
