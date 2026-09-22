from fastapi import FastAPI
from app.domain.schemas import TripQuery

app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/trips/search")
async def search_trip(query: TripQuery):
    return {"message" : "Seacrh is valid!", "data" : "query"}

