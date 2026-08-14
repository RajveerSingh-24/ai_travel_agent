from abc import ABC, abstractmethod

from schemas.booking import BookingResult
from schemas.search import FlightOption, HotelOption
from schemas.travel import TravelConstraints


class BookingProvider(ABC):
    """Interface for providers that book selected travel options."""

    @abstractmethod
    def book(
        self,
        flight: FlightOption,
        hotel: HotelOption,
        constraints: TravelConstraints,
    ) -> BookingResult:
        """Book the selected options and return a provider-independent result."""
