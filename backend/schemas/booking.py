from enum import Enum

from pydantic import BaseModel, Field


class BookingStatus(str, Enum):
    """Possible outcomes of a booking request."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"


class BookingResult(BaseModel):
    """Provider-independent result for a selected flight and hotel booking."""

    booking_id: str = Field(..., min_length=1)
    status: BookingStatus
    selected_flight_id: str = Field(..., min_length=1)
    selected_hotel_id: str = Field(..., min_length=1)
    total_price: float = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
