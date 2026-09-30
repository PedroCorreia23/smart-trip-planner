import pytest
from unittest.mock import AsyncMock

from app.application.trip_search import TripSearchUseCase
from app.domain.schemas import TripQuery, Coordinates, CurrencyInfo, ExchangeRateInfo, WeatherInfo
from app.exceptions import LocationNotFoundError, CurrencyUnavailableError

@pytest.mark.asyncio
async def test_trip_search_success():

    geo_service = AsyncMock()
    weather_service = AsyncMock()
    currency_service = AsyncMock()
    exchange_rate_service = AsyncMock()

    origin_coords = Coordinates(
        lat=38.72,
        lon=-9.14,
        country_code="pt"
    )

    destination_coords = Coordinates(
        lat=40.71,
        lon=-74.00,
        country_code="us"
    )

    origin_currency = CurrencyInfo(
        code="EUR",
        name="Euro",
        symbol="€"
    )

    destination_currency = CurrencyInfo(
        code="USD",
        name="US Dollar",
        symbol="$"
    )

    fake_weather = WeatherInfo(
        time=["2026-10-10"],
        temperature_2m_max=[20.0],
        temperature_2m_min=[10.0],
        precipitation_sum=[0.0]
    )

    fake_exchange_rate = ExchangeRateInfo(
        base="EUR",
        target="USD",
        rate=1.18
    )

    geo_service.get_coordinates.side_effect = [
        origin_coords,
        destination_coords
    ]

    currency_service.get_currency.side_effect = [
        origin_currency,
        destination_currency
    ]

    weather_service.get_weather.return_value = fake_weather
    exchange_rate_service.get_rate.return_value = fake_exchange_rate

    use_case = TripSearchUseCase(
        geocoding_service=geo_service,
        weather_service=weather_service,
        currency_service=currency_service,
        exchange_rate_service=exchange_rate_service
    )

    query = TripQuery(
        origin="Lisboa",
        destination="New York",
        start_date="2026-10-10",
        end_date="2026-10-15"
    )

    result = await use_case.execute(query)

    assert result.origin_coordinates == origin_coords
    assert result.destination_coordinates == destination_coords
    assert result.origin_currency == origin_currency
    assert result.destination_currency == destination_currency
    assert result.weather == fake_weather
    assert result.exchange_rate == fake_exchange_rate

    exchange_rate_service.get_rate.assert_awaited_once_with(
        "EUR",
        "USD"
    )

    geo_service.get_coordinates.assert_any_await("Lisboa")
    geo_service.get_coordinates.assert_any_await("New York")
    assert geo_service.get_coordinates.await_count == 2

    currency_service.get_currency.assert_any_await("pt")
    currency_service.get_currency.assert_any_await("us")
    assert currency_service.get_currency.await_count == 2


@pytest.mark.asyncio
async def test_trip_search_origin_not_found():

    geo_service = AsyncMock()
    weather_service = AsyncMock()
    currency_service = AsyncMock()
    exchange_rate_service = AsyncMock()

    geo_service.get_coordinates.side_effect = [
        None,
        Coordinates(
            lat=40.71,
            lon=-74.00,
            country_code="us"
        )
    ]

    use_case = TripSearchUseCase(
        geocoding_service=geo_service,
        weather_service=weather_service,
        currency_service=currency_service,
        exchange_rate_service=exchange_rate_service
    )

    query = TripQuery(
        origin="CidadeInexistente",
        destination="New York",
        start_date="2026-10-10",
        end_date="2026-10-15"
    )

    with pytest.raises(LocationNotFoundError) as exc:
        await use_case.execute(query)

    assert str(exc.value) == "Origin city not found."


@pytest.mark.asyncio
async def test_trip_search_destination_not_found():

    geo_service = AsyncMock()
    weather_service = AsyncMock()
    currency_service = AsyncMock()
    exchange_rate_service = AsyncMock()

    geo_service.get_coordinates.side_effect = [
        Coordinates(
            lat=38.72,
            lon=-9.14,
            country_code="pt"
        ),
        None
    ]

    use_case = TripSearchUseCase(
        geocoding_service=geo_service,
        weather_service=weather_service,
        currency_service=currency_service,
        exchange_rate_service=exchange_rate_service
    )

    query = TripQuery(
        origin="Lisboa",
        destination="CidadeInexistente",
        start_date="2026-10-10",
        end_date="2026-10-15"
    )

    with pytest.raises(LocationNotFoundError) as exc:
        await use_case.execute(query)

    assert str(exc.value) == "Destination city not found."


@pytest.mark.asyncio
async def test_trip_search_origin_currency_not_found():

    geo_service = AsyncMock()
    weather_service = AsyncMock()
    currency_service = AsyncMock()
    exchange_rate_service = AsyncMock()

    geo_service.get_coordinates.side_effect = [
        Coordinates(
            lat=38.72,
            lon=-9.14,
            country_code="pt"
        ),
        Coordinates(
            lat=40.71,
            lon=-74.00,
            country_code="us"
        )
    ]

    currency_service.get_currency.side_effect = [
        None,
        CurrencyInfo(
            code="USD",
            name="US Dollar",
            symbol="$"
        )
    ]

    use_case = TripSearchUseCase(
        geocoding_service=geo_service,
        weather_service=weather_service,
        currency_service=currency_service,
        exchange_rate_service=exchange_rate_service
    )

    query = TripQuery(
        origin="Lisboa",
        destination="New York",
        start_date="2026-10-10",
        end_date="2026-10-15"
    )

    with pytest.raises(CurrencyUnavailableError) as exc:
        await use_case.execute(query)

    assert str(exc.value) == "Could not retrieve origin currency."


@pytest.mark.asyncio
async def test_trip_search_destination_currency_not_found():

    geo_service = AsyncMock()
    weather_service = AsyncMock()
    currency_service = AsyncMock()
    exchange_rate_service = AsyncMock()

    geo_service.get_coordinates.side_effect = [
        Coordinates(
            lat=38.72,
            lon=-9.14,
            country_code="pt"
        ),
        Coordinates(
            lat=40.71,
            lon=-74.00,
            country_code="us"
        )
    ]

    currency_service.get_currency.side_effect = [
        CurrencyInfo(
            code="EUR",
            name="Euro",
            symbol="€"
        ),
        None
    ]

    use_case = TripSearchUseCase(
        geocoding_service=geo_service,
        weather_service=weather_service,
        currency_service=currency_service,
        exchange_rate_service=exchange_rate_service
    )

    query = TripQuery(
        origin="Lisboa",
        destination="New York",
        start_date="2026-10-10",
        end_date="2026-10-15"
    )

    with pytest.raises(CurrencyUnavailableError) as exc:
        await use_case.execute(query)

    assert str(exc.value) == "Could not retrieve destination currency."


@pytest.mark.asyncio
async def test_trip_search_same_currency():

    geo_service = AsyncMock()
    weather_service = AsyncMock()
    currency_service = AsyncMock()
    exchange_rate_service = AsyncMock()

    origin_coords = Coordinates(
        lat=38.72,
        lon=-9.14,
        country_code="pt"
    )

    destination_coords = Coordinates(
        lat=48.85,
        lon=2.35,
        country_code="fr"
    )

    eur_currency = CurrencyInfo(
        code="EUR",
        name="Euro",
        symbol="€"
    )

    fake_weather = WeatherInfo(
        time=["2026-10-10"],
        temperature_2m_max=[20.0],
        temperature_2m_min=[10.0],
        precipitation_sum=[0.0]
    )

    geo_service.get_coordinates.side_effect = [
        origin_coords,
        destination_coords
    ]

    currency_service.get_currency.side_effect = [
        eur_currency,
        eur_currency
    ]

    weather_service.get_weather.return_value = fake_weather

    use_case = TripSearchUseCase(
        geocoding_service=geo_service,
        weather_service=weather_service,
        currency_service=currency_service,
        exchange_rate_service=exchange_rate_service
    )

    query = TripQuery(
        origin="Lisboa",
        destination="Paris",
        start_date="2026-10-10",
        end_date="2026-10-15"
    )

    result = await use_case.execute(query)

    assert result.exchange_rate == ExchangeRateInfo(
        base="EUR",
        target="EUR",
        rate=1.0
    )

    exchange_rate_service.get_rate.assert_not_awaited()