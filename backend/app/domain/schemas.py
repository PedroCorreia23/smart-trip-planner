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
            raise ValueError("End date can not be previouse to the starting date.")
        return end_date

