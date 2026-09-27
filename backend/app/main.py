from fastapi import FastAPI
from app.domain.schemas import TripQuery
from app.services.geocoding import GeocodingService
from app.services.weather import WeatherService
from fastapi.middleware.cors import CORSMiddleware
from app.services.currency import CurrencyService
from app.services.exchange_rate import ExchangeRateService
from app.application.trip_search import TripSearchUseCase

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

    use_case = TripSearchUseCase(geocoding_service=geo_service, weather_service=weather_service, currency_service=currency_service,
                                    exchange_rate_service=exchange_rate_service)  

    return await use_case.execute(query) 

