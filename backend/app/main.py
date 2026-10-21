import logging

from fastapi import Depends, FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.application.poi_search import POISearchUseCase
from app.application.trip_search import TripSearchUseCase
from app.dependencies import get_poi_search_use_case, get_trip_search_use_case
from app.domain.schemas import POIInfo, TripQuery, TripSearchResponse
from app.exceptions import (
    CurrencyUnavailableError,
    ExternalServiceError,
    LocationNotFoundError,
)
from app.logging_config import configure_logging

configure_logging()

logger = logging.getLogger(__name__)

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Permite o teu frontend Vite
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/pois", response_model=list[POIInfo])
async def search_pois(
    lat: float = Query(..., ge=-90, le=90, description="Latitude of the destination"),
    lon: float = Query(..., ge=-180, le=180, description="Longetiude of the destination"),
    radius: int = Query(default=5000, ge=100, le=10000),
    use_case: POISearchUseCase = Depends(get_poi_search_use_case),
):
    logger.info(
        "Points of interest requested: lat=%s lon=%s radius=%s",
        lat,
        lon,
        radius,
    )
    return await use_case.execute(lat, lon, radius)


@app.post("/trips/search", response_model=TripSearchResponse)
async def search_trip(
    query: TripQuery, use_case: TripSearchUseCase = Depends(get_trip_search_use_case)
):
    logger.info("Trip search requested: origin=%s destination=%s", query.origin, query.destination)
    return await use_case.execute(query)


@app.exception_handler(ExternalServiceError)
async def external_service_error_handler(request: Request, exc: ExternalServiceError):
    logger.error("External service error: %s", exc)
    return JSONResponse(
        status_code=502, content={"detail": "An external service is currently unavailable."}
    )


@app.exception_handler(LocationNotFoundError)
async def location_not_found_handler(request: Request, exc: LocationNotFoundError):
    logger.warning("Location not found: %s", exc)
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(CurrencyUnavailableError)
async def currency_unavailable_handler(request: Request, exc: CurrencyUnavailableError):
    logger.warning("Currency unavailable: %s", exc)
    return JSONResponse(status_code=502, content={"detail": str(exc)})
