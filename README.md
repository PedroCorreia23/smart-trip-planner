# 🌍 Smart Trip Planner (Backend API)

A modern API built with **FastAPI** to orchestrate trip planning. This service acts as a smart intermediary (BFF - Backend for Frontend), receiving trip requests, validating business rules, and integrating with external APIs to provide geographic and weather information.

## ✨ Core Features

* **Trip Validation:** Ensures dates and input data are logically valid using `Pydantic`.
* **Integrated Geocoding:** Converts city names into exact geographic coordinates (OpenStreetMap/Nominatim integration).
* **Weather Forecast:** Provides temperatures and precipitation for the exact days of the trip at the destination (Open-Meteo integration).
* **Resilient Architecture:** Global error handling and standardized HTTP responses.

## 🛠️ Tech Stack

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
* **Validation:** Pydantic (V2)
* **HTTP Requests:** `httpx` (Async)
* **Testing:** Pytest & `unittest.mock`

---

## 🚀 How to Run Locally

### 1. Prerequisites

* Python 3.10+
* Git

### 2. Installation

Clone the repository and enter the backend directory:

```bash
git clone https://github.com/YOUR-USERNAME/smart-trip-planner.git
cd smart-trip-planner/backend
```

Create and activate a virtual environment:

#### Windows

```powershell
python -m venv venv
.\venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Start the Server

Run the FastAPI development server:

```bash
fastapi dev app/main.py
```

### 4. Explore the API (Swagger UI)

FastAPI automatically generates interactive documentation.

Open your browser and visit:

http://127.0.0.1:8000/docs

---

## 🧪 How to Run Tests

The project includes an automated test suite using **mocks** to ensure it doesn't depend on external APIs during execution.

To run the tests:

```bash
# From the backend folder
python -m pytest
```
