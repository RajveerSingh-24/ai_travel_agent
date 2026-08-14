from datetime import date

from schemas.search import FlightOption, HotelOption
from schemas.travel import TravelConstraints
from services.recommendation_service import TravelRecommendationService


def make_flight(
    flight_id: str,
    *,
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
        direct=True,
        duration_minutes=duration_minutes,
    )


def make_hotel(
    hotel_id: str,
    *,
    rating: float = 4.0,
    total_price: float = 800.0,
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


class TestTravelRecommendationService:
    """Tests for deterministic trip-combination recommendations."""

    def setup_method(self):
        self.service = TravelRecommendationService()

    def test_combines_flights_and_hotels_with_correct_total_price(self):
        flight = make_flight("flight-1", price=500.0)
        hotels = [
            make_hotel("hotel-1", total_price=800.0),
            make_hotel("hotel-2", total_price=1000.0),
        ]

        recommendations = self.service.recommend(
            TravelConstraints(), [flight], hotels
        )

        assert len(recommendations) == 2
        assert all(recommendation.flight is flight for recommendation in recommendations)
        assert {recommendation.hotel.id for recommendation in recommendations} == {
            "hotel-1",
            "hotel-2",
        }
        assert {
            recommendation.hotel.id: recommendation.total_price
            for recommendation in recommendations
        } == {"hotel-1": 1300.0, "hotel-2": 1500.0}

    def test_excludes_combinations_over_budget(self):
        flight = make_flight("flight-1", price=400.0)
        hotels = [
            make_hotel("within-budget", total_price=700.0),
            make_hotel("over-budget", total_price=1000.0),
        ]

        recommendations = self.service.recommend(
            TravelConstraints(budget=1200.0), [flight], hotels
        )

        assert [recommendation.hotel.id for recommendation in recommendations] == [
            "within-budget"
        ]
        assert recommendations[0].total_price == 1100.0

    def test_orders_combinations_by_their_ranked_scores(self):
        flights = [
            make_flight("expensive", price=900.0),
            make_flight("cheap", price=400.0),
        ]
        hotels = [make_hotel("hotel")]

        recommendations = self.service.recommend(TravelConstraints(), flights, hotels)

        assert [recommendation.flight.id for recommendation in recommendations] == [
            "cheap",
            "expensive",
        ]
        assert recommendations[0].score > recommendations[1].score

    def test_limits_results_to_top_three_combinations(self):
        flights = [make_flight("flight-1"), make_flight("flight-2", price=600.0)]
        hotels = [make_hotel("hotel-1"), make_hotel("hotel-2", rating=4.5)]

        recommendations = self.service.recommend(TravelConstraints(), flights, hotels)

        assert len(recommendations) == 3

    def test_uses_ids_for_deterministic_tie_breaking(self):
        flights = [make_flight("flight-b"), make_flight("flight-a")]
        hotels = [make_hotel("hotel-b"), make_hotel("hotel-a")]

        recommendations = self.service.recommend(TravelConstraints(), flights, hotels)

        assert [
            (recommendation.flight.id, recommendation.hotel.id)
            for recommendation in recommendations
        ] == [
            ("flight-a", "hotel-a"),
            ("flight-a", "hotel-b"),
            ("flight-b", "hotel-a"),
        ]

    def test_returns_empty_when_flights_or_hotels_are_empty(self):
        flight = make_flight("flight-1")
        hotel = make_hotel("hotel-1")

        assert self.service.recommend(TravelConstraints(), [], [hotel]) == []
        assert self.service.recommend(TravelConstraints(), [flight], []) == []
