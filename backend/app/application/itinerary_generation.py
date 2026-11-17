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
