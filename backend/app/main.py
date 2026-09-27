from fastapi import FastAPI, HTTPException
from app.domain.schemas import TripQuery
from app.services.geocoding import GeocodingService
from app.services.weather import WeatherService
from fastapi.middleware.cors import CORSMiddleware
from app.services.currency import CurrencyService
from app.services.exchange_rate import ExchangeRateService

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
    exchange_rate_service = ExchangeRateService()

    origin_coords = await geo_service.get_coordinates(query.origin)
    destination_coords =  await geo_service.get_coordinates(query.destination)

    if not origin_coords:
        raise HTTPException(status_code=404, detail="Origin city not found.")
    elif not destination_coords:
        raise HTTPException(status_code=404, detail="Destination city not found.")

    origin_currency = await currency_service.get_currency(origin_coords["country_code"])
    destination_currency = await currency_service.get_currency(destination_coords["country_code"])

    if not origin_currency:
        raise HTTPException(status_code=502, detail="Could not retrieve origin currency.")

    if not destination_currency:
        raise HTTPException(status_code=502,detail="Could not retrieve destination currency.")

    if origin_currency["code"] == destination_currency["code"]:
        exchange_rate = {"base": origin_currency["code"],"target": destination_currency["code"],"rate": 1.0}
    else: 
        exchange_rate = await exchange_rate_service.get_rate(origin_currency["code"], destination_currency["code"])

    weather = await weather_service.get_weather(
        lat=destination_coords["lat"],
        lon=destination_coords["lon"],
        start_date=query.start_date,
        end_date=query.end_date
    )
    
    return {"message" : "Trip sucessfully processed",
              "trip_details" : query,
              "origin_coordinates" : origin_coords,
              "destination_coordinates" : destination_coords,
              "weather" : weather,
              "origin_currency" : origin_currency,
              "destination_currency" : destination_currency,
              "exchange_rate" : exchange_rate
    }
