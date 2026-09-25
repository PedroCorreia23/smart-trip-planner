from fastapi import FastAPI, HTTPException
from app.domain.schemas import TripQuery
from app.services.geocoding import GeocodingService
from app.services.weather import WeatherService

app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/trips/search")
async def search_trip(query: TripQuery):
    geo_service = GeocodingService()
    coords =  await geo_service.get_coordinates(query.destination)
    weather_service = WeatherService()

    weather = await weather_service.get_weather(
        lat=coords["lat"],
        lon=coords["lon"],
        start_date=query.start_date,
        end_date=query.end_date
    )

    if not coords:
        raise HTTPException(status_code=404, detail="Destination city not found.")
    
    return {"message" : "Trip sucessfully processed",
             "trip_details" : query,
              "destination_coordinates" : coords,
              "weather" : weather
    }

