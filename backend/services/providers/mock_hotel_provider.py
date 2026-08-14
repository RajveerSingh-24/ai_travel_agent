from datetime import date

from schemas.search import HotelOption
from schemas.travel import TravelConstraints
from services.providers.hotel_provider import HotelProvider


class MockHotelProvider(HotelProvider):
    """Deterministic, offline hotel provider for prototype development."""

    _HOTELS = (
        ("mock-hotel-001", "Grand Plaza", 4.7, 230.0),
        ("mock-hotel-002", "City Suites", 4.3, 170.0),
        ("mock-hotel-003", "Harbor Inn", 3.6, 105.0),
    )

    def search(self, constraints: TravelConstraints) -> list[HotelOption]:
        """Return deterministic hotels filtered by the supplied constraints."""
        nights = self._nights(constraints)
        if not constraints.destination or nights is None:
            return []

        currency = constraints.currency or "USD"
        options = [
            HotelOption(
                id=hotel_id,
                name=name,
                destination=constraints.destination,
                rating=rating,
                price_per_night=price_per_night,
                total_price=price_per_night * nights,
                currency=currency,
            )
            for hotel_id, name, rating, price_per_night in self._HOTELS
        ]

        if constraints.hotel_rating is not None:
            options = [
                option
                for option in options
                if option.rating >= constraints.hotel_rating
            ]
        if constraints.budget is not None:
            options = [
                option for option in options if option.total_price <= constraints.budget
            ]

        return options

    @staticmethod
    def _nights(constraints: TravelConstraints) -> int | None:
        if constraints.duration_days and constraints.duration_days > 0:
            return constraints.duration_days
        if constraints.departure_date and constraints.return_date:
            nights = (constraints.return_date - constraints.departure_date).days
            return nights if nights > 0 else None
        return None
