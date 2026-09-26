from fastapi import FastAPI, HTTPException
from app.domain.schemas import TripQuery
from app.services.geocoding import GeocodingService
from app.services.weather import WeatherService
from fastapi.middleware.cors import CORSMiddleware
from app.services.currency import CurrencyService

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Permite o teu frontend Vite
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/trips/search")
async def search_trip(query: TripQuery):

    geo_service = GeocodingService()
    currency_service = CurrencyService()
    weather_service = WeatherService()

    coords =  await geo_service.get_coordinates(query.destination)

    if not coords:
        raise HTTPException(status_code=404, detail="Destination city not found.")

    currency = await currency_service.get_currency(coords["country_code"])

    weather = await weather_service.get_weather(
        lat=coords["lat"],
        lon=coords["lon"],
        start_date=query.start_date,
        end_date=query.end_date
    )
    
    return {"message" : "Trip sucessfully processed",
             "trip_details" : query,
              "destination_coordinates" : coords,
              "weather" : weather,
              "currency" : currency
    }
