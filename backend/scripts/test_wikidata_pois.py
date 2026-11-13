import asyncio

import httpx

API_URL = "https://www.wikidata.org/w/api.php"

HEADERS = {
    "User-Agent": ("SmartTripPlanner/0.1 (https://github.com/PedroCorreia23/smart-trip-planner)"),
    "Accept": "application/json",
}

PLACES = {
    "Q1773229": "Biblioteca Joanina",
    "Q1580762": "Unknown monument",
}


async def get_entities(client, ids, props):
    response = await client.get(
        API_URL,
        params={
            "action": "wbgetentities",
            "ids": "|".join(ids),
            "props": props,
            "languages": "pt|en|fr",
            "format": "json",
        },
    )
    response.raise_for_status()

    return response.json().get("entities", {})


def get_label(entity, fallback):
    labels = entity.get("labels", {})

    for language in ("pt", "en", "fr"):
        value = labels.get(language, {}).get("value")
        if value:
            return value

    return fallback


def get_claim_values(entity, property_id):
    values = []

    for claim in entity.get("claims", {}).get(property_id, []):
        mainsnak = claim.get("mainsnak", {})

        if mainsnak.get("snaktype") != "value":
            continue

        value = mainsnak.get("datavalue", {}).get("value")

        if value is not None:
            values.append(value)

    return values


async def main():
    try:
        async with httpx.AsyncClient(
            timeout=20.0,
            headers=HEADERS,
        ) as client:
            print("Fetching Coimbra entities...")

            entities = await get_entities(
                client,
                list(PLACES),
                "labels|claims|descriptions",
            )

            type_ids = set()
            place_types = {}

            for place_id in PLACES:
                entity = entities.get(place_id, {})

                ids = {
                    value["id"]
                    for value in get_claim_values(entity, "P31")
                    if isinstance(value, dict) and value.get("id")
                }

                place_types[place_id] = ids
                type_ids.update(ids)

            type_entities = await get_entities(
                client,
                sorted(type_ids),
                "labels",
            )

    except httpx.HTTPError as exc:
        print(f"Request failed: {exc}")
        return

    for place_id, fallback in PLACES.items():
        entity = entities.get(place_id, {})

        print(f"\n--- {place_id} ---")
        print("Name:", get_label(entity, fallback))

        descriptions = entity.get("descriptions", {})
        description = next(
            (descriptions[lang]["value"] for lang in ("pt", "en", "fr") if lang in descriptions),
            "N/A",
        )

        print("Description:", description)

        print("Types:")

        for type_id in sorted(place_types.get(place_id, set())):
            label = get_label(
                type_entities.get(type_id, {}),
                type_id,
            )
            print(f"  - {label} ({type_id})")

        coordinates = get_claim_values(entity, "P625")

        if coordinates:
            for coordinate in coordinates:
                print(
                    "Coordinates:",
                    coordinate.get("latitude"),
                    coordinate.get("longitude"),
                )
        else:
            print("Coordinates: unavailable")


if __name__ == "__main__":
    asyncio.run(main())
