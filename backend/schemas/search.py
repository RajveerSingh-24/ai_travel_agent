from datetime import date

from pydantic import BaseModel, Field, model_validator


class FlightOption(BaseModel):
    """Provider-independent representation of a round-trip flight result."""

    id: str = Field(..., min_length=1, description="Provider-specific flight ID")
    airline: str = Field(..., min_length=1, description="Operating airline name")
    origin: str = Field(..., min_length=1, description="Departure city or airport")
    destination: str = Field(..., min_length=1, description="Arrival city or airport")
    departure_date: date
    return_date: date
    price: float = Field(..., gt=0, description="Total flight price")
    currency: str = Field(..., min_length=3, max_length=3)
    direct: bool
    duration_minutes: int = Field(..., gt=0)

    @model_validator(mode="after")
    def return_date_is_not_before_departure_date(self) -> "FlightOption":
        """Ensure a round-trip result has a valid date range."""
        if self.return_date < self.departure_date:
            raise ValueError("return_date cannot be before departure_date")
        return self


class HotelOption(BaseModel):
    """Provider-independent representation of a hotel search result."""

    id: str = Field(..., min_length=1, description="Provider-specific hotel ID")
    name: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)
    rating: float = Field(..., ge=1, le=5)
    price_per_night: float = Field(..., gt=0)
    total_price: float = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
