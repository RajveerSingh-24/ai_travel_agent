from schemas.booking import BookingResult
from schemas.search import FlightOption, HotelOption
from schemas.travel import TravelConstraints
from services.providers.booking_provider import BookingProvider


class BookingService:
    """Delegates bookings to an injected provider implementation."""

    def __init__(self, booking_provider: BookingProvider):
        self.booking_provider = booking_provider
        self._bookings: dict[str, BookingResult] = {}

    def book(
        self,
        approval_id: str,
        flight: FlightOption,
        hotel: HotelOption,
        constraints: TravelConstraints,
    ) -> BookingResult:
        """Book selected travel options, returning a cached result when present."""
        cached_result = self._bookings.get(approval_id)
        if cached_result is not None:
            return cached_result

        result = self.booking_provider.book(flight, hotel, constraints)
        self._bookings[approval_id] = result
        return result
