from dataclasses import dataclass

from schemas.search import FlightOption, HotelOption
from schemas.travel import TravelConstraints


@dataclass
class RankedFlight:
    """A flight option and its deterministic ranking score."""

    option: FlightOption
    score: float


@dataclass
class RankedHotel:
    """A hotel option and its deterministic ranking score."""

    option: HotelOption
    score: float


class TravelRankingService:
    """Ranks travel search results using normalized, explainable factors."""

    def rank_flights(
        self,
        constraints: TravelConstraints,
        flights: list[FlightOption],
    ) -> list[RankedFlight]:
        """Rank flights by directness preference, price, and duration."""
        if not flights:
            return []

        price_scores = self._lower_is_better([flight.price for flight in flights])
        duration_scores = self._lower_is_better(
            [flight.duration_minutes for flight in flights]
        )

        ranked_flights = []
        for flight, price_score, duration_score in zip(
            flights, price_scores, duration_scores
        ):
            if constraints.direct_flight is True:
                score = (
                    0.60 * float(flight.direct)
                    + 0.25 * price_score
                    + 0.15 * duration_score
                )
            else:
                score = 0.60 * price_score + 0.40 * duration_score
            ranked_flights.append(RankedFlight(option=flight, score=score))

        return sorted(
            ranked_flights,
            key=lambda ranked: (-ranked.score, ranked.option.id),
        )

    def rank_hotels(
        self,
        constraints: TravelConstraints,
        hotels: list[HotelOption],
    ) -> list[RankedHotel]:
        """Rank hotels by rating and total price."""
        if not hotels:
            return []

        rating_scores = self._higher_is_better([hotel.rating for hotel in hotels])
        price_scores = self._lower_is_better(
            [hotel.total_price for hotel in hotels]
        )
        ranked_hotels = [
            RankedHotel(
                option=hotel,
                score=0.60 * rating_score + 0.40 * price_score,
            )
            for hotel, rating_score, price_score in zip(
                hotels, rating_scores, price_scores
            )
        ]

        return sorted(
            ranked_hotels,
            key=lambda ranked: (-ranked.score, ranked.option.id),
        )

    @staticmethod
    def _lower_is_better(values: list[float | int]) -> list[float]:
        """Min-max normalize values so the smallest value receives a score of 1."""
        minimum = min(values)
        maximum = max(values)
        if minimum == maximum:
            return [1.0] * len(values)
        return [(maximum - value) / (maximum - minimum) for value in values]

    @staticmethod
    def _higher_is_better(values: list[float | int]) -> list[float]:
        """Min-max normalize values so the largest value receives a score of 1."""
        minimum = min(values)
        maximum = max(values)
        if minimum == maximum:
            return [1.0] * len(values)
        return [(value - minimum) / (maximum - minimum) for value in values]
