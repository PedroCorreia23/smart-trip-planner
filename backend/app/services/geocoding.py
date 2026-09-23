import httpx

class GeocodingService:
    async def get_coordinates(self, city_name: str):
        url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1" 
        headers = {"User-Agent": "SmartTripPlanner/0.1"}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            data = response.json()
            
            if not data:
                return None # Caso a cidade não seja encontrada                   

            latitude = float(data[0]["lat"])
            longitude = float(data[0]["lon"])

            return {"lat": latitude, "lon": longitude}
