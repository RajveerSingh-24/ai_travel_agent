from datetime import date

import pytest

from schemas.travel import TravelConstraints
from services.providers.flight_provider import FlightProvider
from services.providers.hotel_provider import HotelProvider
from services.providers.mock_flight_provider import MockFlightProvider
from services.providers.mock_hotel_provider import MockHotelProvider


class TestProviderInterfaces:
    """Tests for the provider abstractions."""

    def test_flight_provider_is_abstract(self):
        with pytest.raises(TypeError):
            FlightProvider()

    def test_hotel_provider_is_abstract(self):
        with pytest.raises(TypeError):
            HotelProvider()


class TestMockFlightProvider:
    """Tests for deterministic offline flight results."""

    def test_returns_matching_flights_with_derived_return_date(self):
        constraints = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date=date(2026, 9, 1),
            duration_days=7,
            travellers=2,
            currency="EUR",
        )

        results = MockFlightProvider().search(constraints)

        assert len(results) == 3
        assert all(result.origin == "New York" for result in results)
        assert all(result.destination == "Paris" for result in results)
        assert all(result.departure_date == date(2026, 9, 1) for result in results)
        assert all(result.return_date == date(2026, 9, 8) for result in results)
        assert all(result.currency == "EUR" for result in results)
        assert results[0].price == 840.0

    def test_filters_direct_flights_and_budget(self):
        constraints = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date=date(2026, 9, 1),
            return_date=date(2026, 9, 8),
            travellers=2,
            direct_flight=True,
            budget=900.0,
        )

        results = MockFlightProvider().search(constraints)

        assert [result.id for result in results] == ["mock-flight-001"]
        assert all(result.direct for result in results)
        assert all(result.price <= 900.0 for result in results)

    def test_returns_no_flights_without_a_complete_route_and_stay(self):
        constraints = TravelConstraints(origin="New York", destination="Paris")

        assert MockFlightProvider().search(constraints) == []


class TestMockHotelProvider:
    """Tests for deterministic offline hotel results."""

    def test_returns_matching_hotels_with_total_price_for_stay(self):
        constraints = TravelConstraints(
            destination="Paris",
            departure_date=date(2026, 9, 1),
            return_date=date(2026, 9, 8),
            currency="EUR",
        )

        results = MockHotelProvider().search(constraints)

        assert len(results) == 3
        assert all(result.destination == "Paris" for result in results)
        assert all(result.currency == "EUR" for result in results)
        assert results[0].price_per_night == 230.0
        assert results[0].total_price == 1610.0

    def test_filters_minimum_rating_and_budget(self):
        constraints = TravelConstraints(
            destination="Paris",
            departure_date=date(2026, 9, 1),
            duration_days=7,
            hotel_rating=4.5,
            budget=1700.0,
        )

        results = MockHotelProvider().search(constraints)

        assert [result.id for result in results] == ["mock-hotel-001"]
        assert all(result.rating >= 4.5 for result in results)
        assert all(result.total_price <= 1700.0 for result in results)

    def test_returns_no_hotels_without_destination_and_stay(self):
        constraints = TravelConstraints(destination="Paris")

        assert MockHotelProvider().search(constraints) == []
