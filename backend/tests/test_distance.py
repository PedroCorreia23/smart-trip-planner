import pytest

from app.domain.distance import haversine_distance


def test_haversine_same_coordinates():
    distance = haversine_distance(
        48.8566,
        2.3522,
        48.8566,
        2.3522,
    )

    assert distance == 0


def test_haversine_lisbon_to_porto():
    distance = haversine_distance(
        38.7223,
        -9.1393,
        41.1579,
        -8.6291,
    )

    assert distance == pytest.approx(274, abs=2)


def test_haversine_symmetry():
    lisbon_to_porto = haversine_distance(
        38.7223,
        -9.1393,
        41.1579,
        -8.6291,
    )

    porto_to_lisbon = haversine_distance(
        41.1579,
        -8.6291,
        38.7223,
        -9.1393,
    )

    assert lisbon_to_porto == pytest.approx(porto_to_lisbon)
