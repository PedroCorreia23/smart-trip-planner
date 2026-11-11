import logging
from html import unescape
from html.parser import HTMLParser

import httpx

from app.config import settings
from app.domain.schemas import POIImageInfo
from app.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def get_text(self) -> str:
        return "".join(self.parts).strip()


def clean_html_text(value: str | None) -> str | None:
    if not value:
        return None

    parser = HTMLTextExtractor()
    parser.feed(unescape(value))

    return parser.get_text() or None


class POIImageService:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

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
            response = await self.client.get(
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

    async def get_commons_image(self, filename: str) -> POIImageInfo | None:
        url = "https://commons.wikimedia.org/w/api.php"

        params = {
            "action": "query",
            "format": "json",
            "prop": "imageinfo",
            "titles": f"File:{filename}",
            "iiprop": "url|extmetadata",
            "iiurlwidth": 600,
        }

        headers = {
            "User-Agent": settings.USER_AGENT,
        }

        try:
            response = await self.client.get(
                url,
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

            pages = data.get("query", {}).get("pages", {})

            for page in pages.values():
                image_info = page.get("imageinfo", [])

                if not image_info:
                    continue

                info = image_info[0]

                image_url = info.get("url")

                if not image_url:
                    continue

                thumbnail_url = info.get("thumburl")
                description_url = info.get("descriptionurl")

                metadata = info.get("extmetadata", {})

                author = clean_html_text(metadata.get("Artist", {}).get("value"))
                license_name = metadata.get("LicenseShortName", {}).get("value")

                return POIImageInfo(
                    url=image_url,
                    thumbnail_url=thumbnail_url,
                    author=author,
                    license=license_name,
                    description_url=description_url,
                )

            return None

        except httpx.HTTPStatusError as exc:
            logger.error(
                "Wikimedia Commons returned HTTP error: status=%s",
                exc.response.status_code,
            )
            raise ExternalServiceError("Wikimedia Commons returned an HTTP error.") from exc

        except httpx.RequestError as exc:
            logger.error("Wikimedia Commons request failed: %s", exc)
            raise ExternalServiceError("Wikimedia Commons service is unavailable.") from exc
