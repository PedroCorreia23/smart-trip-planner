from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.domain.schemas import TripQuery, TripSearchResponse
from app.services.geocoding import GeocodingService
from app.services.weather import WeatherService
from fastapi.middleware.cors import CORSMiddleware
from app.services.currency import CurrencyService
from app.services.exchange_rate import ExchangeRateService
from app.application.trip_search import TripSearchUseCase
from app.exceptions import ExternalServiceError
from app.exceptions import LocationNotFoundError, CurrencyUnavailableError

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

@app.post("/trips/search", response_model=TripSearchResponse)
async def search_trip(query: TripQuery):

    geo_service = GeocodingService()
    currency_service = CurrencyService()
    weather_service = WeatherService()
    exchange_rate_service = ExchangeRateService()

    use_case = TripSearchUseCase(geocoding_service=geo_service, weather_service=weather_service, currency_service=currency_service,
                                    exchange_rate_service=exchange_rate_service)  

    return await use_case.execute(query) 

@app.exception_handler(ExternalServiceError)
async def external_service_error_handler(request: Request, exc: ExternalServiceError):
    
    return JSONResponse(
        status_code=502,
        content={
            "detail": "An external service is currently unavailable."
        }
    )

@app.exception_handler(LocationNotFoundError)
async def location_not_found_handler(
    request: Request,
    exc: LocationNotFoundError
):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )

@app.exception_handler(CurrencyUnavailableError)
async def currency_unavailable_handler(
    request: Request,
    exc: CurrencyUnavailableError
):
    return JSONResponse(
        status_code=502,
        content={"detail": str(exc)}
    )