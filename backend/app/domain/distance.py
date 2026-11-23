import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    earth_radius_km = 6371

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    distance_km = 2 * math.asin(math.sqrt(a)) * earth_radius_km

    return distance_km
