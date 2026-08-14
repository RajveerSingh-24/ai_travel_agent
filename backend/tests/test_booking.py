from datetime import date
from unittest.mock import Mock

import pytest

from schemas.booking import BookingResult, BookingStatus
from schemas.search import FlightOption, HotelOption
from schemas.travel import TravelConstraints
from services.booking_service import BookingService
from services.providers.booking_provider import BookingProvider
from services.providers.mock_booking_provider import MockBookingProvider


def make_flight() -> FlightOption:
    return FlightOption(
        id="flight-1",
        airline="Example Air",
        origin="New York",
        destination="Paris",
        departure_date=date(2026, 9, 1),
        return_date=date(2026, 9, 8),
        price=500.0,
        currency="USD",
        direct=True,
        duration_minutes=435,
    )


def make_hotel(destination: str = "Paris") -> HotelOption:
    return HotelOption(
        id="hotel-1",
        name="Example Hotel",
        destination=destination,
        rating=4.5,
        price_per_night=120.0,
        total_price=840.0,
        currency="USD",
    )


def make_constraints() -> TravelConstraints:
    return TravelConstraints(
        origin="New York",
        destination="Paris",
        departure_date=date(2026, 9, 1),
        return_date=date(2026, 9, 8),
        travellers=2,
        currency="USD",
    )


class TestBookingProvider:
    """Tests for the booking provider abstraction and mock implementation."""

    def test_booking_provider_is_abstract(self):
        with pytest.raises(TypeError):
            BookingProvider()

    def test_mock_provider_confirms_valid_selection_with_booking_data(self):
        result = MockBookingProvider().book(
            make_flight(),
            make_hotel(),
            make_constraints(),
        )

        assert result.booking_id == "mock-booking-flight-1-hotel-1"
        assert result.status is BookingStatus.CONFIRMED
        assert result.selected_flight_id == "flight-1"
        assert result.selected_hotel_id == "hotel-1"
        assert result.total_price == 1340.0
        assert result.currency == "USD"

    def test_mock_provider_returns_failed_result_for_invalid_selection(self):
        result = MockBookingProvider().book(
            make_flight(),
            make_hotel(destination="Tokyo"),
            make_constraints(),
        )

        assert result.status is BookingStatus.FAILED
        assert result.booking_id == "mock-booking-failed-flight-1-hotel-1"


class TestBookingService:
    """Tests for delegation through BookingService."""

    def test_delegates_to_injected_booking_provider(self):
        provider = Mock(spec=BookingProvider)
        expected_result = BookingResult(
            booking_id="booking-1",
            status=BookingStatus.CONFIRMED,
            selected_flight_id="flight-1",
            selected_hotel_id="hotel-1",
            total_price=1340.0,
            currency="USD",
        )
        provider.book.return_value = expected_result
        flight = make_flight()
        hotel = make_hotel()
        constraints = make_constraints()
        service = BookingService(provider)

        result = service.book(flight, hotel, constraints)

        provider.book.assert_called_once_with(flight, hotel, constraints)
        assert result is expected_result
