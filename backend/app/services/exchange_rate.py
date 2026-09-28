import httpx
from app.exceptions import ExternalServiceError

class ExchangeRateService:
    async def get_rate(self, base_currency: str, target_currency: str):
        url=f"https://api.frankfurter.dev/v2/rate/{base_currency.upper()}/{target_currency.upper()}"
        headers = {"User-Agent": "SmartTripPlanner/0.1"}

        try:    
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                if "rate" not in data or data["rate"] is None:
                    return None

                rate = data["rate"]
                base = data["base"]
                target = data["quote"]

                return {
                    "rate" : rate,
                    "base" : base,
                    "target" : target
                }
            
        except httpx.HTTPStatusError as exc:
            raise ExternalServiceError("Exchange rate service returned an HTTP error.") from exc 

        except httpx.RequestError as exc:
            raise ExternalServiceError("Exchange rate service is unavailable.") from exc
            




