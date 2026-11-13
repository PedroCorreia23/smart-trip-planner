import argparse
import asyncio
import time

import httpx

from app.exceptions import ExternalServiceError
from app.services.wikidata_poi import WikidataPOIService

CITIES = {
    "coimbra": (40.2033, -8.4103),
    "paris": (48.8566, 2.3522),
    "lisbon": (38.7223, -9.1393),
    "london": (51.5074, -0.1278),
}

CATEGORIES = (
    "museum",
    "monument",
    "park",
    "attraction",
)

HEADERS = {
    "User-Agent": ("SmartTripPlanner/0.1 (https://github.com/PedroCorreia23/smart-trip-planner)"),
    "Accept": "application/json",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Validate Wikidata POI discovery")

    parser.add_argument(
        "--city",
        choices=CITIES,
        default="coimbra",
    )

    parser.add_argument(
        "--category",
        choices=CATEGORIES,
        default="monument",
    )

    parser.add_argument(
        "--radius",
        type=int,
        default=5000,
        help="Search radius in meters",
    )

    return parser.parse_args()


async def main():
    args = parse_args()

    lat, lon = CITIES[args.city]

    print("\n--- WIKIDATA POI VALIDATION ---")
    print(f"City: {args.city}")
    print(f"Category: {args.category}")
    print(f"Coordinates: {lat}, {lon}")
    print(f"Radius: {args.radius} meters")

    start = time.perf_counter()

    try:
        async with httpx.AsyncClient(
            headers=HEADERS,
            timeout=httpx.Timeout(
                45.0,
                connect=10.0,
            ),
        ) as client:
            service = WikidataPOIService(client)

            pois = await service.get_pois(
                lat=lat,
                lon=lon,
                radius=args.radius,
                category=args.category,
            )

    except ExternalServiceError as exc:
        elapsed = time.perf_counter() - start

        print(f"\nService error: {exc}")
        print(f"Elapsed time: {elapsed:.2f}s")
        return

    except ValueError as exc:
        print(f"\nInvalid input: {exc}")
        return

    elapsed = time.perf_counter() - start

    print(f"\nTotal POIs: {len(pois)}")
    print(f"Response time: {elapsed:.2f}s")

    print("\n--- RESULTS ---")

    if not pois:
        print("No POIs found.")
        return

    for index, poi in enumerate(pois, start=1):
        print(
            f"{index}. {poi.name} | "
            f"ID: {poi.wikidata_id} | "
            f"Coordinates: {poi.lat}, {poi.lon} | "
            f"Category: {poi.category}"
        )


if __name__ == "__main__":
    asyncio.run(main())
