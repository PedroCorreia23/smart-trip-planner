from pydantic import BaseModel, field_validator
from datetime import date

class TripQuery(BaseModel):
    origin: str
    destination: str
    start_date: date
    end_date: date

    @field_validator("end_date")
    @classmethod
    def future_date_invalide(cls, end_date, info):
        start_date = info.data.get("start_date")

        if start_date and end_date < start_date:
            raise ValueError(
                "End date can not be previouse to the starting date."
            )

        return end_date

class Coordinates(BaseModel):
    lat: float
    lon: float
    country_code: str

class CurrencyInfo(BaseModel):
    code: str
    name: str
    symbol: str

class ExchangeRateInfo(BaseModel):
    base: str
    target: str
    rate: float

class WeatherInfo(BaseModel):
    time: list[str]
    temperature_2m_max: list[float]
    temperature_2m_min: list[float]
    precipitation_sum: list[float]


class TripSearchResponse(BaseModel):
    message: str
    trip_details: TripQuery
    origin_coordinates: Coordinates
    destination_coordinates: Coordinates
    weather: WeatherInfo
    origin_currency: CurrencyInfo
    destination_currency: CurrencyInfo
    exchange_rate: ExchangeRateInfo