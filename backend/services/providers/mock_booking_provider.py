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
        if constraints.origin and flight.origin != constraints.origin:
            return False
        if constraints.destination and (
            flight.destination != constraints.destination
            or hotel.destination != constraints.destination
        ):
            return False
        if constraints.departure_date and flight.departure_date != constraints.departure_date:
            return False
        if constraints.return_date and flight.return_date != constraints.return_date:
            return False
        if (
            constraints.duration_days
            and constraints.departure_date
            and flight.return_date
            != constraints.departure_date + timedelta(days=constraints.duration_days)
        ):
            return False
        if constraints.currency and flight.currency != constraints.currency:
            return False
        if constraints.budget is not None and total_price > constraints.budget:
            return False
        return True
