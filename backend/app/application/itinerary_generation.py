from app.domain.distance import haversine_distance


def find_nearest_poi(current_poi, remaining_pois):
    menor_distancia = float("inf")
    poi_mais_proximo = None

    for poi in remaining_pois:
        distancia = haversine_distance(
            current_poi.lat,
            current_poi.lon,
            poi.lat,
            poi.lon,
        )

        if distancia < menor_distancia:
            menor_distancia = distancia
            poi_mais_proximo = poi

    return poi_mais_proximo

def calculate_daily_capacity(num_pois: int, num_days: int) -> list[int]:
    if num_days <= 0:
        raise ValueError("Number of days must be positive.")

    base, remainder = divmod(num_pois, num_days)

    return [
        base + (1 if day < remainder else 0)
        for day in range(num_days)
    ]