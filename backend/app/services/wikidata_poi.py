import logging
import re

import httpx

from app.domain.schemas import POIInfo
from app.exceptions import ExternalServiceError
from app.services.wikidata_query import build_poi_query

logger = logging.getLogger(__name__)

SPARQL_URL = "https://query.wikidata.org/sparql"
WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"

POINT_PATTERN = re.compile(r"^Point\(([-+]?\d+(?:\.\d+)?) ([-+]?\d+(?:\.\d+)?)\)$")


def parse_coordinates(value: str) -> tuple[float, float] | None:
    match = POINT_PATTERN.fullmatch(value)

    if not match:
        return None

    lon = float(match.group(1))
    lat = float(match.group(2))

    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None

    return lat, lon


class WikidataPOIService:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def get_pois(
        self,
        lat: float,
        lon: float,
        radius: int = 5000,
        category: str = "museum",
    ) -> list[POIInfo]:
        query = build_poi_query(
            lat=lat,
            lon=lon,
            radius=radius,
            category=category,
        )

        try:
            response = await self.client.get(
                SPARQL_URL,
                params={
                    "query": query,
                    "format": "json",
                },
            )
            response.raise_for_status()

            bindings = response.json()["results"]["bindings"]

            candidates = {}

            for item in bindings:
                wikidata_id = item["place"]["value"].rsplit("/", 1)[-1]

                if not re.fullmatch(r"Q[1-9]\d*", wikidata_id):
                    continue

                coordinates = parse_coordinates(item["location"]["value"])

                if coordinates is None:
                    continue

                if wikidata_id in candidates:
                    continue

                poi_lat, poi_lon = coordinates

                candidates[wikidata_id] = {
                    "lat": poi_lat,
                    "lon": poi_lon,
                }

            if not candidates:
                return []

            names = await self.get_names(list(candidates))

            pois = []

            for wikidata_id, location in candidates.items():
                name = names.get(wikidata_id)

                if not name or name == wikidata_id:
                    continue

                pois.append(
                    POIInfo(
                        id=wikidata_id,
                        wikidata_id=wikidata_id,
                        name=name,
                        category=category,
                        lat=location["lat"],
                        lon=location["lon"],
                    )
                )

            return pois

        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            logger.error("Wikidata POI request failed: %s", exc)
            raise ExternalServiceError("Wikidata POI service is unavailable.") from exc

    async def get_names(
        self,
        wikidata_ids: list[str],
    ) -> dict[str, str]:
        names = {}

        for start in range(0, len(wikidata_ids), 40):
            batch = wikidata_ids[start : start + 40]

            response = await self.client.get(
                WIKIDATA_API_URL,
                params={
                    "action": "wbgetentities",
                    "ids": "|".join(batch),
                    "props": "labels",
                    "languages": "pt|en|fr",
                    "format": "json",
                },
            )
            response.raise_for_status()

            entities = response.json()["entities"]

            for wikidata_id, entity in entities.items():
                labels = entity.get("labels", {})

                name = next(
                    (
                        labels[language]["value"]
                        for language in ("pt", "en", "fr")
                        if labels.get(language, {}).get("value")
                    ),
                    None,
                )

                if name:
                    names[wikidata_id] = name

        return names

    async def get_wikidata_id(self, place_id: str) -> str | None:
        if re.fullmatch(r"Q[1-9]\d*", place_id):
            return place_id

        return None
