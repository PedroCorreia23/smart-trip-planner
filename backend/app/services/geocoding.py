import httpx
from app.exceptions import ExternalServiceError
from app.domain.schemas import Coordinates

class GeocodingService:
    async def get_coordinates(self, city_name: str):
        url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1&addressdetails=1" 
        headers = {"User-Agent": "SmartTripPlanner/0.1"}

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    return None # Caso a cidade não seja encontrada                   

                latitude = float(data[0]["lat"])
                longitude = float(data[0]["lon"])
                country_code = data[0]["address"]["country_code"]

                return Coordinates(lat=latitude, lon=longitude, country_code=country_code)
                
        except httpx.HTTPStatusError as exc:
            raise ExternalServiceError("Geocoding service returned an HTTP error.") from exc 
        except httpx.RequestError as exc:
            raise ExternalServiceError("Geocoding service is unavailable.") from exc