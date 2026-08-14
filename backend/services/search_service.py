from dataclasses import dataclass

from schemas.search import FlightOption, HotelOption
from schemas.travel import TravelConstraints
from services.providers.flight_provider import FlightProvider
from services.providers.hotel_provider import HotelProvider


@dataclass
class TravelSearchResult:
    """Flight and hotel options returned for a travel search."""

    flights: list[FlightOption]
    hotels: list[HotelOption]


class TravelSearchService:
    """Coordinates independent searches through injected travel providers."""

    def __init__(self, flight_provider: FlightProvider, hotel_provider: HotelProvider):
        self.flight_provider = flight_provider
        self.hotel_provider = hotel_provider

    def search(self, constraints: TravelConstraints) -> TravelSearchResult:
        """Search for flight and hotel options using the supplied constraints."""
        flights = self.flight_provider.search(constraints)
        hotels = self.hotel_provider.search(constraints)

        return TravelSearchResult(flights=flights, hotels=hotels)
