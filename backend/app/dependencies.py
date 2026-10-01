from app.application.trip_search import TripSearchUseCase
from app.services.geocoding import GeocodingService
from app.services.weather import WeatherService
from app.services.currency import CurrencyService
from app.services.exchange_rate import ExchangeRateService

def get_trip_search_use_case() -> TripSearchUseCase:
    return TripSearchUseCase(
        geocoding_service=GeocodingService(),
        weather_service=WeatherService(),
        currency_service=CurrencyService(),
        exchange_rate_service=ExchangeRateService()
    )