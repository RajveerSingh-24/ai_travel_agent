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
        self._cache = {}

    def search(self, constraints: TravelConstraints) -> TravelSearchResult:
        """Search for flight and hotel options using the supplied constraints."""
        cache_key = constraints.model_dump_json()
        if cache_key in self._cache:
            return self._cache[cache_key]

        flights = self.flight_provider.search(constraints)
        hotels = self.hotel_provider.search(constraints)
        
        # Normalize to USD to avoid mismatched currencies between flight and hotel
        for f in flights:
            if f.currency == "INR":
                f.price = f.price / 83.0
                f.currency = "USD"
            elif f.currency == "EUR":
                f.price = f.price * 1.10
                f.currency = "USD"
                
        for h in hotels:
            if h.currency == "INR":
                h.price_per_night = h.price_per_night / 83.0
                h.total_price = h.total_price / 83.0
                h.currency = "USD"
            elif h.currency == "EUR":
                h.price_per_night = h.price_per_night * 1.10
                h.total_price = h.total_price * 1.10
                h.currency = "USD"

        result = TravelSearchResult(flights=flights, hotels=hotels)
        self._cache[cache_key] = result
        return result
