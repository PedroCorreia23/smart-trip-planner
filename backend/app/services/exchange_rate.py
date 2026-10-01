import logging

import httpx

from app.config import settings
from app.domain.schemas import ExchangeRateInfo
from app.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class ExchangeRateService:
    async def get_rate(self, base_currency: str, target_currency: str):
        url = f"{settings.FRANKFURTER_BASE_URL}/dev/v2/rate/{base_currency.upper()}/{target_currency.upper()}"
        headers = {"User-Agent": settings.USER_AGENT}

        try:
            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                if "rate" not in data or data["rate"] is None:
                    return None

                return ExchangeRateInfo(base=data["base"], target=data["quote"], rate=data["rate"])

        except httpx.HTTPStatusError as exc:
            logger.error("Exchange API returned HTTP error: status=%s", exc.response.status_code)
            raise ExternalServiceError("Exchange rate service returned an HTTP error.") from exc
        except httpx.RequestError as exc:
            logger.error("Exchange API  request failed: %s", exc)
            raise ExternalServiceError("Exchange rate service is unavailable.") from exc
