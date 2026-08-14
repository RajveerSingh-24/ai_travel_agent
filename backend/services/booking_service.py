from schemas.booking import BookingResult
from schemas.search import FlightOption, HotelOption
from schemas.travel import TravelConstraints
from services.providers.booking_provider import BookingProvider


class BookingService:
    """Delegates bookings to an injected provider implementation."""

    def __init__(self, booking_provider: BookingProvider):
        self.booking_provider = booking_provider

    def book(
        self,
        flight: FlightOption,
        hotel: HotelOption,
        constraints: TravelConstraints,
    ) -> BookingResult:
        """Book selected travel options through the configured provider."""
        return self.booking_provider.book(flight, hotel, constraints)
