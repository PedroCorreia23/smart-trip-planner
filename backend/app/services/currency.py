import httpx, logging
from app.exceptions import ExternalServiceError
from app.domain.schemas import CurrencyInfo
from app.config import settings

logger = logging.getLogger(__name__)

class CurrencyService:
    async def get_currency(self, country_code: str):
        url=f"{settings.COUNTRIES_BASE_URL}/alpha/{country_code.upper()}"
        headers = {"User-Agent": settings.USER_AGENT}

        try:
            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                if "currencies" not in data or not data["currencies"]:
                    return None

                currency = data["currencies"][0]

                return CurrencyInfo(code=currency["code"], name=currency["name"], symbol=currency["symbol"])
        except httpx.HTTPStatusError as exc:
            logger.error("Currency API returned HTTP error: status=%s", exc.response.status_code)
            raise ExternalServiceError("Currency service returned an HTTP error.") from exc
        except httpx.RequestError as exc:
            logger.error("Currency API  request failed: %s", exc)
            raise ExternalServiceError("Currency service is unavailable.") from exc