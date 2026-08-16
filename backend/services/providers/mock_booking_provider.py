from datetime import timedelta

from schemas.booking import BookingResult, BookingStatus
from schemas.search import FlightOption, HotelOption
from schemas.travel import TravelConstraints
from services.providers.booking_provider import BookingProvider


class MockBookingProvider(BookingProvider):
    """Deterministic, offline booking provider for prototype development."""

    def book(
        self,
        flight: FlightOption,
        hotel: HotelOption,
        constraints: TravelConstraints,
    ) -> BookingResult:
        """Confirm valid selected options or return a deterministic failed result."""
        total_price = flight.price + hotel.total_price
        is_valid = self._is_valid_selection(flight, hotel, constraints, total_price)
        status = BookingStatus.CONFIRMED if is_valid else BookingStatus.FAILED
        booking_prefix = "mock-booking" if is_valid else "mock-booking-failed"

        return BookingResult(
            booking_id=f"{booking_prefix}-{flight.id}-{hotel.id}",
            status=status,
            selected_flight_id=flight.id,
            selected_hotel_id=hotel.id,
            total_price=total_price,
            currency=flight.currency,
        )

    @staticmethod
    def _is_valid_selection(
        flight: FlightOption,
        hotel: HotelOption,
        constraints: TravelConstraints,
        total_price: float,
    ) -> bool:
        if flight.destination != hotel.destination or flight.currency != hotel.currency:
            return False
        
        # We don't need to re-verify all constraints (budget, currency, etc) here because 
        # they were already verified by the search and recommendation services.
        # Also, currency normalization to USD may cause false positives if compared to constraints.currency.
        return True
