# 🌍 Smart Trip Planner

Smart Trip Planner is a backend API built with FastAPI that aggregates travel-related information from multiple external services.

Given an origin, destination and travel dates, the API validates the trip and retrieves geographic information, weather data, currencies and exchange rates.


## ✨ Features

- Trip validation with Pydantic
- Geocoding for origin and destination
- Weather forecast for the destination
- Currency detection for origin and destination
- Exchange rate calculation
- Async external API integrations
- Typed application models
- Centralized error handling
- Dependency injection with FastAPI
- Environment-based configuration
- Application and service logging
- Automated tests with mocks
- Ruff linting and formatting
- GitHub Actions CI


## 🏗️ Architecture

The backend follows a modular monolithic architecture.

Main layers:

- API Layer — FastAPI endpoints and HTTP concerns
- Application Layer — use cases and orchestration
- Domain Models — Pydantic models and contracts
- External Services — integrations with third-party APIs

External integrations are isolated behind dedicated services.


## 🛠️ Tech Stack

- Python 3.12
- FastAPI
- Pydantic v2
- pydantic-settings
- httpx
- Pytest
- pytest-cov
- Ruff
- GitHub Actions


## 🌐 External APIs

- Nominatim / OpenStreetMap — geocoding
- Open-Meteo — weather
- countries.dev — currency information
- Frankfurter — exchange rates


## 🚀 Run Locally

### 1. Clone the repository

git clone https://github.com/PedroCorreia23/smart-trip-planner.git
cd smart-trip-planner/backend


### 2. Create a virtual environment

Windows:

python -m venv .venv
.\.venv\Scripts\activate


Linux / macOS:

python3 -m venv .venv
source .venv/bin/activate


### 3. Install dependencies

pip install -r requirements.txt


### 4. Environment configuration

Copy the example environment file.

Windows PowerShell:

Copy-Item .env.example .env


Linux / macOS:

cp .env.example .env


Default values are already provided for the external services.


### 5. Start the API

fastapi dev app/main.py


Swagger documentation:

http://127.0.0.1:8000/docs


## 🔎 Main Endpoint

POST /trips/search


Example request:

{
  "origin": "Lisbon",
  "destination": "Paris",
  "start_date": "2026-10-10",
  "end_date": "2026-10-15"
}


The response includes:

- Origin coordinates
- Destination coordinates
- Destination weather
- Origin currency
- Destination currency
- Exchange rate


## 🧪 Tests

Run the complete test suite:

python -m pytest


Run tests with coverage:

python -m pytest --cov=app --cov-report=term-missing


Current test suite:

27 automated tests

Current coverage:

Approximately 99%


## ✅ Code Quality

Run Ruff linting:

ruff check app tests


Check formatting:

ruff format --check app tests


Format automatically:

ruff format app tests


## 🔄 Continuous Integration

GitHub Actions automatically runs the backend CI pipeline on pushes and pull requests to the main branch.

The pipeline validates:

- Ruff linting
- Ruff formatting
- Pytest automated tests


## 📌 V1 Scope

Implemented:

RF01 — Define trip

The user can provide:

- Origin
- Destination
- Start date
- End date


RF02 — Geographic location

The system obtains geographic coordinates and country information for the origin and destination using Nominatim / OpenStreetMap.


RF03 — Weather information

The system obtains weather information for the destination during the selected travel period using Open-Meteo.


RF05 — Currency information

The system determines the currencies used at both the origin and destination.


RF06 — Currency conversion

The system retrieves the exchange rate between the origin currency and destination currency.

When both locations use the same currency, the exchange rate is set to 1.0.


Deferred:

RF04 — Distance between origin and destination

This requirement was intentionally deferred from V1 because displaying the direct geographic distance between two cities does not currently provide enough value to the main use case.

Distance calculation may become more useful in future versions when optimizing routes between points of interest within a destination.


## 🧱 Backend Structure

The backend is organized into different responsibilities.

API Layer

Responsible for:

- HTTP endpoints
- FastAPI
- Dependency injection
- HTTP responses
- Exception handlers


Application Layer

Responsible for:

- Application use cases
- Trip search orchestration
- Service contracts / protocols


Domain Layer

Responsible for:

- Pydantic models
- Typed application data
- Trip validation


External Services

Responsible for integrations with:

- Geocoding API
- Weather API
- Currency API
- Exchange rate API


Configuration

Application configuration is centralized using pydantic-settings.

Configuration can be provided using environment variables or a .env file.

The repository contains a .env.example file with the expected configuration structure.


## ⚠️ Error Handling

External API errors are isolated from the application logic.

The application defines custom exceptions such as:

- ExternalServiceError
- LocationNotFoundError
- CurrencyUnavailableError

FastAPI exception handlers convert these application errors into appropriate HTTP responses.

Examples:

Location not found → HTTP 404

External service unavailable → HTTP 502


## 📊 Logging

The application uses Python's logging system.

Logging is implemented for:

- Trip search requests
- Location errors
- Currency errors
- External API failures

Sensitive configuration values are not included in logs.


## 🧪 Testing Strategy

Tests use mocks so that the automated test suite does not depend on real external APIs.

The test suite covers:

- Trip validation
- Geocoding
- Weather
- Currency retrieval
- Exchange rates
- Trip search orchestration
- Error handling
- FastAPI endpoints
- Dependency injection behavior

Current coverage is approximately 99%.


## 🗺️ Future Versions

V2 — Points of Interest

Allow users to search and select relevant places to visit at the destination.


V3 — Itinerary Generation

Automatically generate an itinerary using the selected points of interest.


Future improvements may include:

- Route optimization between locations
- Opening hours
- Visit duration
- User preferences
- Saved trips
- Persistent storage
- PostgreSQL integration


## 📂 Repository

GitHub:

https://github.com/PedroCorreia23/smart-trip-planner