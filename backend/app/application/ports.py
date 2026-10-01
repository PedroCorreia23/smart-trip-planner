from datetime import date
from typing import Protocol

from app.domain.schemas import (
    Coordinates,
    CurrencyInfo,
    ExchangeRateInfo,
    WeatherInfo,
)


class GeocodingPort(Protocol):
    async def get_coordinates(self, city_name: str) -> Coordinates | None: ...


class WeatherPort(Protocol):
    async def get_weather(
        self, lat: float, lon: float, start_date: date, end_date: date
    ) -> WeatherInfo | None: ...


class CurrencyPort(Protocol):
    async def get_currency(self, country_code: str) -> CurrencyInfo | None: ...


class ExchangeRatePort(Protocol):
    async def get_rate(
        self, base_currency: str, target_currency: str
    ) -> ExchangeRateInfo | None: ...
