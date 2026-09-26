import httpx

class CurrencyService:
    async def get_currency(self, country_code: str):
        url=f"https://countries.dev/alpha/{country_code.upper()}"
        headers = {"User-Agent": "SmartTripPlanner/0.1"}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            data = response.json()

            if "currencies" not in data or not data["currencies"]:
                return None

            currency = data["currencies"][0]

            return currency
