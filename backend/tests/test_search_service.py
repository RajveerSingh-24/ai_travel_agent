from datetime import date
from unittest.mock import Mock

from schemas.search import FlightOption, HotelOption
from schemas.travel import TravelConstraints
from services.providers.flight_provider import FlightProvider
from services.providers.hotel_provider import HotelProvider
from services.search_service import TravelSearchService


class TestTravelSearchService:
    """Tests for provider orchestration in TravelSearchService."""

    def test_passes_same_constraints_to_both_providers(self):
        flight_provider = Mock(spec=FlightProvider)
        hotel_provider = Mock(spec=HotelProvider)
        flight_provider.search.return_value = []
        hotel_provider.search.return_value = []
        constraints = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date=date(2026, 9, 1),
            return_date=date(2026, 9, 8),
            travellers=2,
        )
        service = TravelSearchService(flight_provider, hotel_provider)

        service.search(constraints)

        flight_provider.search.assert_called_once_with(constraints)
        hotel_provider.search.assert_called_once_with(constraints)

    def test_returns_provider_results_unchanged(self):
        flights = [
            FlightOption(
                id="flight-123",
                airline="Example Air",
                origin="New York",
                destination="Paris",
                departure_date=date(2026, 9, 1),
                return_date=date(2026, 9, 8),
                price=850.0,
                currency="USD",
                direct=True,
                duration_minutes=435,
            )
        ]
        hotels = [
            HotelOption(
                id="hotel-123",
                name="Example Hotel",
                destination="Paris",
                rating=4.5,
                price_per_night=180.0,
                total_price=1260.0,
                currency="USD",
            )
        ]
        flight_provider = Mock(spec=FlightProvider)
        hotel_provider = Mock(spec=HotelProvider)
        flight_provider.search.return_value = flights
        hotel_provider.search.return_value = hotels
        service = TravelSearchService(flight_provider, hotel_provider)

        result = service.search(TravelConstraints())

        assert result.flights is flights
        assert result.hotels is hotels
