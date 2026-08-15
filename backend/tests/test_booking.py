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
    """Tests for delegation and idempotency through BookingService."""

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

        result = service.book("approval-1", flight, hotel, constraints)

        provider.book.assert_called_once_with(flight, hotel, constraints)
        assert result is expected_result

    def test_first_booking_calls_provider_and_stores_result(self):
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
        service = BookingService(provider)
        flight = make_flight()
        hotel = make_hotel()
        constraints = make_constraints()

        result = service.book("approval-1", flight, hotel, constraints)

        provider.book.assert_called_once_with(flight, hotel, constraints)
        assert result is expected_result
        assert service._bookings["approval-1"] is expected_result

    def test_repeated_booking_returns_same_result_without_calling_provider(self):
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
        service = BookingService(provider)
        flight = make_flight()
        hotel = make_hotel()
        constraints = make_constraints()

        first_result = service.book("approval-1", flight, hotel, constraints)
        second_result = service.book("approval-1", flight, hotel, constraints)

        provider.book.assert_called_once()
        assert second_result is first_result

    def test_failed_booking_is_cached_and_returned_unchanged_on_repeat(self):
        provider = Mock(spec=BookingProvider)
        failed_result = BookingResult(
            booking_id="booking-failed-1",
            status=BookingStatus.FAILED,
            selected_flight_id="flight-1",
            selected_hotel_id="hotel-1",
            total_price=1340.0,
            currency="USD",
        )
        provider.book.return_value = failed_result
        service = BookingService(provider)
        flight = make_flight()
        hotel = make_hotel(destination="Tokyo")
        constraints = make_constraints()

        first_result = service.book("approval-1", flight, hotel, constraints)
        second_result = service.book("approval-1", flight, hotel, constraints)

        provider.book.assert_called_once()
        assert first_result.status is BookingStatus.FAILED
        assert second_result is first_result

    def test_different_approvals_create_independent_bookings(self):
        provider = Mock(spec=BookingProvider)
        provider.book.side_effect = [
            BookingResult(
                booking_id="booking-1",
                status=BookingStatus.CONFIRMED,
                selected_flight_id="flight-1",
                selected_hotel_id="hotel-1",
                total_price=1340.0,
                currency="USD",
            ),
            BookingResult(
                booking_id="booking-2",
                status=BookingStatus.CONFIRMED,
                selected_flight_id="flight-1",
                selected_hotel_id="hotel-1",
                total_price=1340.0,
                currency="USD",
            ),
        ]
        service = BookingService(provider)
        flight = make_flight()
        hotel = make_hotel()
        constraints = make_constraints()

        first_result = service.book("approval-1", flight, hotel, constraints)
        second_result = service.book("approval-2", flight, hotel, constraints)

        assert provider.book.call_count == 2
        assert first_result.booking_id == "booking-1"
        assert second_result.booking_id == "booking-2"
