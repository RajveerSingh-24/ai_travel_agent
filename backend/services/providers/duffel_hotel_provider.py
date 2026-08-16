import os
from datetime import date
from typing import Any, Optional
from urllib import response

import requests
from dotenv import load_dotenv

from schemas.search import HotelOption
from schemas.travel import TravelConstraints
from services.location_service import LocationService
from services.providers.hotel_provider import HotelProvider

load_dotenv()


class DuffelHotelProvider(HotelProvider):
    """Hotel provider backed by the Duffel Stays API."""

    BASE_URL = "https://api.duffel.com"

    def __init__(
        self,
        api_client: Optional[Any] = None,
        location_service: Optional[LocationService] = None,
        api_token: Optional[str] = None,
    ):
        self.api_client = api_client or requests.Session()
        self.location_service = location_service or LocationService()

        if api_token is None:
            api_token = os.getenv("DUFFEL_API_TOKEN")

        self.api_token = api_token

    def search(self, constraints: TravelConstraints) -> list[HotelOption]:
        """Search Duffel for available accommodation."""

        check_out_date = self._return_date(constraints)

        if (
            not constraints.destination
            or not constraints.departure_date
            or not check_out_date
            or not constraints.travellers
        ):
            return []

        if not self.api_token:
            raise ValueError(
                "DUFFEL_API_TOKEN not found in environment variables"
            )

        coordinates = self.location_service.resolve_coordinates(
            constraints.destination
        )

        payload = {
            "data": {
                "location": {
                    "radius": 25,
                    "geographic_coordinates": {
                        "latitude": coordinates["latitude"],
                        "longitude": coordinates["longitude"],
                    },
                },
                "check_in_date": constraints.departure_date.isoformat(),
                "check_out_date": check_out_date.isoformat(),
                "guests": [
                    {"type": "adult"}
                    for _ in range(constraints.travellers)
                ],
                "rooms": 1,
                "accommodation": {
                    "fetch_rates": False,
                },
            }
        }

        response = self.api_client.post(
            f"{self.BASE_URL}/stays/search",
            json=payload,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Duffel-Version": "v2",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()
        results = data.get("data", {}).get("results", [])

        hotels = []

        for result in results:
            hotel = self._map_result(
                result=result,
                constraints=constraints,
            )

            if hotel is None:
                continue

            if (
                constraints.hotel_rating is not None
                and hotel.rating < constraints.hotel_rating
            ):
                continue

            if (
                constraints.budget is not None
                and hotel.total_price > constraints.budget
            ):
                continue

            hotels.append(hotel)

        return hotels

    def _map_result(
        self,
        result: dict,
        constraints: TravelConstraints,
    ) -> Optional[HotelOption]:
        """Convert a Duffel accommodation search result into HotelOption."""

        accommodation = result.get("accommodation") or {}

        hotel_id = accommodation.get("id")
        hotel_name = accommodation.get("name")

        if not hotel_id or not hotel_name:
            return None

        try:
            total_price = float(result["cheapest_rate_total_amount"])
        except (KeyError, TypeError, ValueError):
            return None

        currency = result.get("cheapest_rate_currency")

        if not currency:
            return None

        rating = accommodation.get("rating")

        if rating is None:
            rating = 0

        try:
            rating = float(rating)
        except (TypeError, ValueError):
            return None

        nights = self._nights(
            constraints.departure_date,
            self._return_date(constraints),
        )

        if nights <= 0:
            return None

        price_per_night = total_price / nights

        return HotelOption(
            id=str(hotel_id),
            name=hotel_name,
            destination=constraints.destination,
            rating=rating,
            price_per_night=price_per_night,
            total_price=total_price,
            currency=currency,
        )

    @staticmethod
    def _return_date(
        constraints: TravelConstraints,
    ) -> Optional[date]:
        """Determine checkout date from explicit date or trip duration."""

        if constraints.return_date:
            return constraints.return_date

        if (
            constraints.departure_date
            and constraints.duration_days
            and constraints.duration_days > 0
        ):
            from datetime import timedelta

            return constraints.departure_date + timedelta(
                days=constraints.duration_days
            )

        return None

    @staticmethod
    def _nights(
        check_in: Optional[date],
        check_out: Optional[date],
    ) -> int:
        """Calculate the number of nights in the stay."""

        if not check_in or not check_out:
            return 0

        return (check_out - check_in).days