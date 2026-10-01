from app.application.ports import (
    CurrencyPort,
    ExchangeRatePort,
    GeocodingPort,
    WeatherPort,
)
from app.domain.schemas import ExchangeRateInfo, TripQuery, TripSearchResponse
from app.exceptions import CurrencyUnavailableError, LocationNotFoundError


class TripSearchUseCase:
    def __init__(
        self,
        geocoding_service: GeocodingPort,
        weather_service: WeatherPort,
        currency_service: CurrencyPort,
        exchange_rate_service: ExchangeRatePort,
    ):

        self.geocoding_service = geocoding_service
        self.weather_service = weather_service
        self.currency_service = currency_service
        self.exchange_rate_service = exchange_rate_service

    async def execute(self, query: TripQuery):

        origin_coords = await self.geocoding_service.get_coordinates(query.origin)
        destination_coords = await self.geocoding_service.get_coordinates(query.destination)

        if not origin_coords:
            raise LocationNotFoundError("Origin city not found.")
        if not destination_coords:
            raise LocationNotFoundError("Destination city not found.")

        origin_currency = await self.currency_service.get_currency(origin_coords.country_code)
        destination_currency = await self.currency_service.get_currency(
            destination_coords.country_code
        )

        if not origin_currency:
            raise CurrencyUnavailableError("Could not retrieve origin currency.")

        if not destination_currency:
            raise CurrencyUnavailableError("Could not retrieve destination currency.")

        weather = await self.weather_service.get_weather(
            lat=destination_coords.lat,
            lon=destination_coords.lon,
            start_date=query.start_date,
            end_date=query.end_date,
        )

        if origin_currency.code == destination_currency.code:
            exchange_rate = ExchangeRateInfo(
                base=origin_currency.code, target=destination_currency.code, rate=1.0
            )
        else:
            exchange_rate = await self.exchange_rate_service.get_rate(
                origin_currency.code, destination_currency.code
            )

        return TripSearchResponse(
            message="Trip successfully processed",
            trip_details=query,
            origin_coordinates=origin_coords,
            destination_coordinates=destination_coords,
            weather=weather,
            origin_currency=origin_currency,
            destination_currency=destination_currency,
            exchange_rate=exchange_rate,
        )
