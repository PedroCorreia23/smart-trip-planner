import logging

import httpx

from app.config import settings
from app.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class POIImageService:
    async def get_image(self, wikidata_id: str) -> str | None:
        url = "https://www.wikidata.org/w/api.php"

        params = {
            "action": "wbgetentities",
            "ids": wikidata_id,
            "props": "claims",
            "format": "json",
        }

        headers = {
            "User-Agent": settings.USER_AGENT,
        }

        try:
            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

            entity = data.get("entities", {}).get(wikidata_id, {})
            images = entity.get("claims", {}).get("P18", [])

            if not images:
                return None

            mainsnak = images[0].get("mainsnak", {})

            datavalue = mainsnak.get("datavalue", {})

            return datavalue.get("value")

        except httpx.HTTPStatusError as exc:
            logger.error(
                "Wikidata returned HTTP error: status=%s",
                exc.response.status_code,
            )
            raise ExternalServiceError("Wikidata returned an HTTP error.") from exc

        except httpx.RequestError as exc:
            logger.error("Wikidata request failed: %s", exc)
            raise ExternalServiceError("Wikidata service is unavailable.") from exc
