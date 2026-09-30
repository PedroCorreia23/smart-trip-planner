import httpx
from app.exceptions import ExternalServiceError
from app.domain.schemas import ExchangeRateInfo
from app.config import settings

class ExchangeRateService:
    async def get_rate(self, base_currency: str, target_currency: str):
        url=f"{settings.FRANKFURTER_BASE_URL}/dev/v2/rate/{base_currency.upper()}/{target_currency.upper()}"
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
            raise ExternalServiceError("Exchange rate service returned an HTTP error.") from exc 

        except httpx.RequestError as exc:
            raise ExternalServiceError("Exchange rate service is unavailable.") from exc
            




