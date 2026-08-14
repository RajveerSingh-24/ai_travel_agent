from datetime import date, timedelta

from schemas.search import FlightOption
from schemas.travel import TravelConstraints
from services.providers.flight_provider import FlightProvider


class MockFlightProvider(FlightProvider):
    """Deterministic, offline flight provider for prototype development."""

    _FLIGHTS = (
        ("mock-flight-001", "Atlas Air", 420.0, True, 465),
        ("mock-flight-002", "Nimbus Airlines", 315.0, False, 640),
        ("mock-flight-003", "Horizon Airways", 570.0, True, 450),
    )

    def search(self, constraints: TravelConstraints) -> list[FlightOption]:
        """Return deterministic flights filtered by the supplied constraints."""
        return_date = self._return_date(constraints)
        if (
            not constraints.origin
            or not constraints.destination
            or not constraints.departure_date
            or not return_date
        ):
            return []

        currency = constraints.currency or "USD"
        travellers = constraints.travellers or 1
        options = [
            FlightOption(
                id=flight_id,
                airline=airline,
                origin=constraints.origin,
                destination=constraints.destination,
                departure_date=constraints.departure_date,
                return_date=return_date,
                price=price_per_traveller * travellers,
                currency=currency,
                direct=direct,
                duration_minutes=duration_minutes,
            )
            for flight_id, airline, price_per_traveller, direct, duration_minutes in self._FLIGHTS
        ]

        if constraints.direct_flight is True:
            options = [option for option in options if option.direct]
        if constraints.budget is not None:
            options = [option for option in options if option.price <= constraints.budget]

        return options

    @staticmethod
    def _return_date(constraints: TravelConstraints) -> date | None:
        if constraints.return_date:
            return constraints.return_date
        if constraints.departure_date and constraints.duration_days and constraints.duration_days > 0:
            return constraints.departure_date + timedelta(days=constraints.duration_days)
        return None
