from abc import ABC, abstractmethod

from schemas.search import HotelOption
from schemas.travel import TravelConstraints


class HotelProvider(ABC):
    """Interface for providers that search for hotel options."""

    @abstractmethod
    def search(self, constraints: TravelConstraints) -> list[HotelOption]:
        """Return hotel options that satisfy the supplied constraints."""
