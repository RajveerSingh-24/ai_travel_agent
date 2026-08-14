from dataclasses import dataclass
from typing import Optional

from schemas.search import FlightOption, HotelOption
from schemas.travel import TravelConstraints
from services.ranking_service import TravelRankingService


@dataclass
class TravelRecommendation:
    """A complete flight and hotel combination for a trip."""

    flight: FlightOption
    hotel: HotelOption
    total_price: float
    score: float


class TravelRecommendationService:
    """Builds deterministic trip combinations from ranked search options."""

    def __init__(self, ranking_service: Optional[TravelRankingService] = None):
        self.ranking_service = ranking_service or TravelRankingService()

    def recommend(
        self,
        constraints: TravelConstraints,
        flights: list[FlightOption],
        hotels: list[HotelOption],
    ) -> list[TravelRecommendation]:
        """Return the top three ranked flight and hotel combinations."""
        if not flights or not hotels:
            return []

        ranked_flights = self.ranking_service.rank_flights(constraints, flights)
        ranked_hotels = self.ranking_service.rank_hotels(constraints, hotels)
        recommendations = []

        for ranked_flight in ranked_flights:
            for ranked_hotel in ranked_hotels:
                total_price = ranked_flight.option.price + ranked_hotel.option.total_price
                if (
                    constraints.budget is not None
                    and total_price > constraints.budget
                ):
                    continue
                recommendations.append(
                    TravelRecommendation(
                        flight=ranked_flight.option,
                        hotel=ranked_hotel.option,
                        total_price=total_price,
                        score=(ranked_flight.score + ranked_hotel.score) / 2,
                    )
                )

        return sorted(
            recommendations,
            key=lambda recommendation: (
                -recommendation.score,
                recommendation.flight.id,
                recommendation.hotel.id,
            ),
        )[:3]
