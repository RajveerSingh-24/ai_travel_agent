from abc import ABC, abstractmethod

from schemas.search import FlightOption
from schemas.travel import TravelConstraints


class FlightProvider(ABC):
    """Interface for providers that search for flight options."""

    @abstractmethod
    def search(self, constraints: TravelConstraints) -> list[FlightOption]:
        """Return flight options that satisfy the supplied constraints."""
