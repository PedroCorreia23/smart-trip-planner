from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    NOMINATIM_BASE_URL: str = "https://nominatim.openstreetmap.org"
    WEATHER_BASE_URL: str = "https://api.open-meteo.com"
    COUNTRIES_BASE_URL: str = "https://countries.dev"
    FRANKFURTER_BASE_URL: str = "https://api.frankfurter.dev"

    OVERPASS_BASE_URL: str = "https://overpass-api.de/api"
    OVERPASS_TIMEOUT: float = 30.0

    HTTP_TIMEOUT: float = 5.0
    USER_AGENT: str = "SmartTripPlanner/0.1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
