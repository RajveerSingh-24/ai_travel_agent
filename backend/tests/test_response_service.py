from datetime import date

from schemas.search import FlightOption, HotelOption
from schemas.travel import TravelConstraints
from services.recommendation_service import TravelRecommendation
from services.response_service import TravelResponseService


def make_recommendation(
    flight_id: str,
    hotel_id: str,
    *,
    airline: str = "Atlas Air",
    direct: bool = True,
    hotel_name: str = "Grand Plaza",
    rating: float = 4.7,
    total_price: float = 1350.0,
    score: float = 0.9,
) -> TravelRecommendation:
    flight = FlightOption(
        id=flight_id,
        airline=airline,
        origin="New York",
        destination="Paris",
        departure_date=date(2026, 9, 1),
        return_date=date(2026, 9, 8),
        price=500.0,
        currency="USD",
        direct=direct,
        duration_minutes=435,
    )
    hotel = HotelOption(
        id=hotel_id,
        name=hotel_name,
        destination="Paris",
        rating=rating,
        price_per_night=170.0,
        total_price=850.0,
        currency="USD",
    )
    return TravelRecommendation(
        flight=flight,
        hotel=hotel,
        total_price=total_price,
        score=score,
    )


class TestTravelResponseService:
    """Tests for user-facing recommendation response formatting."""

    def setup_method(self):
        self.service = TravelResponseService()

    def test_formats_complete_recommendation(self):
        response = self.service.format_recommendations(
            TravelConstraints(currency="USD"),
            [make_recommendation("flight-1", "hotel-1")],
        )

        assert "Best overall option:" in response
        assert "1. Atlas Air — direct flight (2026-09-01 to 2026-09-08)" in response
        assert "Hotel: Grand Plaza (4.7/5)" in response
        assert "Total trip price: USD 1350.00" in response

    def test_formats_empty_recommendations_gracefully(self):
        response = self.service.format_recommendations(TravelConstraints(), [])

        assert response == "No travel recommendations are available for the current constraints."

    def test_preserves_order_for_multiple_recommendations(self):
        first = make_recommendation(
            "flight-2",
            "hotel-2",
            airline="Second Airline",
            direct=False,
            hotel_name="Second Hotel",
            score=0.2,
        )
        second = make_recommendation(
            "flight-1",
            "hotel-1",
            airline="First Airline",
            hotel_name="First Hotel",
            score=0.9,
        )

        response = self.service.format_recommendations(
            TravelConstraints(),
            [first, second],
        )

        assert "Other recommended options:" in response
        assert "1. Second Airline — connecting flight" in response
        assert "2. First Airline — direct flight" in response
        assert response.index("Second Airline") < response.index("First Airline")
