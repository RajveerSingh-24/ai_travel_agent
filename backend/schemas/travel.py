from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class TravelConstraints(BaseModel):
    """Structured travel constraints extracted from natural language."""

    origin: Optional[str] = Field(None, description="Departure city or airport")
    destination: Optional[str] = Field(
        None, description="Destination city or airport"
    )
    departure_date: Optional[date] = Field(
        None, description="Departure date (YYYY-MM-DD)"
    )
    return_date: Optional[date] = Field(
        None, description="Return date for round trips (YYYY-MM-DD)"
    )
    duration_days: Optional[int] = Field(
        None, description="Total trip duration in days"
    )
    travellers: Optional[int] = Field(
        None, description="Number of travellers", ge=1, le=100
    )
    budget: Optional[float] = Field(
        None, description="Total budget in specified currency"
    )
    currency: Optional[str] = Field(
        None, description="Currency code (e.g., USD, EUR)"
    )
    direct_flight: Optional[bool] = Field(
        None, description="Prefer direct flights only"
    )
    hotel_rating: Optional[float] = Field(
        None, description="Minimum hotel star rating (1-5)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "origin": "New York",
                "destination": "Paris",
                "departure_date": "2026-09-01",
                "return_date": "2026-09-15",
                "duration_days": 14,
                "travellers": 2,
                "budget": 5000.0,
                "currency": "USD",
                "direct_flight": True,
                "hotel_rating": 4.0,
            }
        }
