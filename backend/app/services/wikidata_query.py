POI_TYPES = {
    "museum": [
        "Q17431399",
        "Q207694",
        "Q3329412",
        "Q33506",
    ],
    "monument": [
        "Q2319498",
        "Q1440300",
        "Q1440476",
        "Q143912",
        "Q56242215",
        "Q120560",
        "Q317557",
        "Q2977",
        "Q44613",
    ],
    "park": [
        "Q1107656",
        "Q22746",
        "Q56478984",
    ],
    "attraction": [
        "Q570116",
        "Q1329623",
        "Q54050",
    ],
}


def build_poi_query(
    lat: float,
    lon: float,
    radius: int,
    category: str,
    limit: int = 20,
) -> str:
    if category not in POI_TYPES:
        raise ValueError(f"Unsupported POI category: {category}")

    if not -90 <= lat <= 90:
        raise ValueError("Invalid latitude")

    if not -180 <= lon <= 180:
        raise ValueError("Invalid longitude")

    if radius <= 0:
        raise ValueError("Radius must be positive")

    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    radius_km = radius / 1000

    type_values = "\n".join(f"wd:{type_id}" for type_id in POI_TYPES[category])

    return f"""
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX bd: <http://www.bigdata.com/rdf#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>

SELECT DISTINCT ?place ?location ?sitelinks
WHERE {{
    SERVICE wikibase:around {{
        ?place wdt:P625 ?location .
        bd:serviceParam
            wikibase:center "Point({lon} {lat})"^^geo:wktLiteral ;
            wikibase:radius "{radius_km}" .
    }}

    VALUES ?type {{
        {type_values}
    }}

    ?place wdt:P31 ?type .
    ?place wikibase:sitelinks ?sitelinks .
}}
ORDER BY DESC(?sitelinks)
LIMIT {limit}
"""
