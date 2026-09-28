import httpx
from app.exceptions import ExternalServiceError

class CurrencyService:
    async def get_currency(self, country_code: str):
        url=f"https://countries.dev/alpha/{country_code.upper()}"
        headers = {"User-Agent": "SmartTripPlanner/0.1"}

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                if "currencies" not in data or not data["currencies"]:
                    return None

                currency = data["currencies"][0]

                return currency
        except httpx.HTTPStatusError as exc:
            raise ExternalServiceError("Currency service returned an HTTP error.") from exc
        except httpx.RequestError as exc:
            raise ExternalServiceError("Currency service is unavailable.") from exc