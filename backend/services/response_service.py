from schemas.travel import TravelConstraints
from services.recommendation_service import TravelRecommendation


class TravelResponseService:
    """Formats ranked travel recommendations for a user-facing response."""

    def format_recommendations(
        self,
        constraints: TravelConstraints,
        recommendations: list[TravelRecommendation],
    ) -> str:
        """Format recommendations in their supplied deterministic order."""
        if not recommendations:
            return "No travel recommendations are available for the current constraints."

        response_parts = []
        for index, recommendation in enumerate(recommendations, start=1):
            if index == 1:
                response_parts.append("Best overall option:")
            elif index == 2:
                response_parts.append("Other recommended options:")

            flight = recommendation.flight
            hotel = recommendation.hotel
            flight_type = "direct" if flight.direct else "connecting"
            currency = constraints.currency or flight.currency
            response_parts.append(
                f"{index}. {flight.airline} — {flight_type} flight "
                f"({flight.departure_date.isoformat()} to {flight.return_date.isoformat()})"
            )
            response_parts.append(f"   Hotel: {hotel.name} ({hotel.rating}/5)")
            response_parts.append(
                f"   Total trip price: {currency} {recommendation.total_price:.2f}"
            )

        return "\n".join(response_parts)
