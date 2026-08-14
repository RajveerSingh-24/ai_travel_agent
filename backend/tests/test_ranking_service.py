from datetime import date

from schemas.search import FlightOption, HotelOption
from schemas.travel import TravelConstraints
from services.ranking_service import TravelRankingService


def make_flight(
    flight_id: str,
    *,
    direct: bool = True,
    price: float = 500.0,
    duration_minutes: int = 500,
) -> FlightOption:
    return FlightOption(
        id=flight_id,
        airline="Example Air",
        origin="New York",
        destination="Paris",
        departure_date=date(2026, 9, 1),
        return_date=date(2026, 9, 8),
        price=price,
        currency="USD",
        direct=direct,
        duration_minutes=duration_minutes,
    )


def make_hotel(
    hotel_id: str,
    *,
    rating: float = 4.0,
    total_price: float = 1000.0,
) -> HotelOption:
    return HotelOption(
        id=hotel_id,
        name="Example Hotel",
        destination="Paris",
        rating=rating,
        price_per_night=total_price / 5,
        total_price=total_price,
        currency="USD",
    )


class TestTravelRankingService:
    """Tests for deterministic, normalized travel search ranking."""

    def setup_method(self):
        self.service = TravelRankingService()

    def test_prefers_direct_flights_when_requested(self):
        flights = [
            make_flight("direct", direct=True, price=900.0, duration_minutes=700),
            make_flight("connecting", direct=False, price=400.0, duration_minutes=400),
        ]

        ranked = self.service.rank_flights(
            TravelConstraints(direct_flight=True), flights
        )

        assert [result.option.id for result in ranked] == ["direct", "connecting"]

    def test_prefers_lower_flight_price_when_other_factors_match(self):
        flights = [
            make_flight("expensive", price=800.0),
            make_flight("cheap", price=400.0),
        ]

        ranked = self.service.rank_flights(TravelConstraints(), flights)

        assert [result.option.id for result in ranked] == ["cheap", "expensive"]

    def test_prefers_shorter_flight_duration_when_other_factors_match(self):
        flights = [
            make_flight("long", duration_minutes=700),
            make_flight("short", duration_minutes=400),
        ]

        ranked = self.service.rank_flights(TravelConstraints(), flights)

        assert [result.option.id for result in ranked] == ["short", "long"]

    def test_prefers_higher_hotel_rating_when_prices_match(self):
        hotels = [
            make_hotel("lower-rated", rating=3.5),
            make_hotel("higher-rated", rating=4.8),
        ]

        ranked = self.service.rank_hotels(TravelConstraints(), hotels)

        assert [result.option.id for result in ranked] == ["higher-rated", "lower-rated"]

    def test_prefers_lower_hotel_price_when_ratings_match(self):
        hotels = [
            make_hotel("expensive", total_price=1400.0),
            make_hotel("cheap", total_price=900.0),
        ]

        ranked = self.service.rank_hotels(TravelConstraints(), hotels)

        assert [result.option.id for result in ranked] == ["cheap", "expensive"]

    def test_uses_option_id_for_deterministic_tie_breaking(self):
        flights = [make_flight("flight-b"), make_flight("flight-a")]
        hotels = [make_hotel("hotel-b"), make_hotel("hotel-a")]

        ranked_flights = self.service.rank_flights(TravelConstraints(), flights)
        ranked_hotels = self.service.rank_hotels(TravelConstraints(), hotels)

        assert [result.option.id for result in ranked_flights] == [
            "flight-a",
            "flight-b",
        ]
        assert [result.option.id for result in ranked_hotels] == ["hotel-a", "hotel-b"]

    def test_returns_empty_rankings_for_empty_results(self):
        constraints = TravelConstraints()

        assert self.service.rank_flights(constraints, []) == []
        assert self.service.rank_hotels(constraints, []) == []
