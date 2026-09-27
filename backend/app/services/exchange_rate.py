import httpx

class ExchangeRateService:
    async def get_rate(self, base_currency: str, target_currency: str):
        url=f"https://api.frankfurter.dev/v2/rate/{base_currency.upper()}/{target_currency.upper()}"
        headers = {"User-Agent": "SmartTripPlanner/0.1"}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
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
            

