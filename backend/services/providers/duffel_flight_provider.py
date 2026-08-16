import os
from dotenv import load_dotenv
from datetime import date
from typing import Any, Optional

import requests

from schemas.search import FlightOption
from schemas.travel import TravelConstraints
from services.location_service import LocationService
from services.providers.flight_provider import FlightProvider

load_dotenv()

class DuffelFlightProvider(FlightProvider):
    """Flight provider backed by the Duffel API."""

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

    def search(self, constraints: TravelConstraints) -> list[FlightOption]:
        """Search Duffel for round-trip flight offers."""

        return_date = self._return_date(constraints)

        if (
            not constraints.origin
            or not constraints.destination
            or not constraints.departure_date
            or not return_date
            or not constraints.travellers
        ):
            return []

        if not self.api_token:
            raise ValueError(
                "DUFFEL_API_TOKEN not found in environment variables"
            )

        origin = self.location_service.resolve(constraints.origin)
        destination = self.location_service.resolve(constraints.destination)

        slices = [
            {
                "origin": origin,
                "destination": destination,
                "departure_date": constraints.departure_date.isoformat(),
            },
            {
                "origin": destination,
                "destination": origin,
                "departure_date": return_date.isoformat(),
            },
        ]

        passengers = [
            {"type": "adult"}
            for _ in range(constraints.travellers)
        ]

        payload = {
            "data": {
                "slices": slices,
                "passengers": passengers,
                "cabin_class": "economy",
            }
        }

        if constraints.direct_flight is True:
            payload["data"]["max_connections"] = 0

        response = self.api_client.post(
            f"{self.BASE_URL}/air/offer_requests",
            json=payload,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Duffel-Version": "v2",
                "Content-Type": "application/json",
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        offers = data.get("data", {}).get("offers", [])

        results = []

        for offer in offers:
            option = self._map_offer(
                offer=offer,
                constraints=constraints,
            )

            if option is None:
                continue

            if (
                constraints.budget is not None
                and option.price > constraints.budget
            ):
                continue

            results.append(option)

        return results

    def _map_offer(
        self,
        offer: dict,
        constraints: TravelConstraints,
    ) -> Optional[FlightOption]:
        """Convert a Duffel offer into the provider-independent model."""

        slices = offer.get("slices", [])

        if len(slices) < 2:
            return None

        outbound = slices[0]
        inbound = slices[1]

        outbound_segments = outbound.get("segments", [])
        inbound_segments = inbound.get("segments", [])

        if not outbound_segments or not inbound_segments:
            return None

        outbound_first = outbound_segments[0]
        inbound_first = inbound_segments[0]

        airline = (
            outbound_first
            .get("operating_carrier", {})
            .get("name")
        )

        if not airline:
            return None

        try:
            price = float(offer["total_amount"])
        except (KeyError, TypeError, ValueError):
            return None

        currency = offer.get("total_currency")

        if not currency:
            return None

        departure_date = self._parse_date(
            outbound_first.get("departing_at")
        )
        return_date = self._parse_date(
            inbound_first.get("departing_at")
        )

        if departure_date is None or return_date is None:
            return None

        direct = (
            len(outbound_segments) == 1
            and len(inbound_segments) == 1
        )

        duration_minutes = self._duration_minutes(outbound)

        if duration_minutes is None:
            return None

        return FlightOption(
            id=str(offer.get("id", "")),
            airline=airline,
            origin=constraints.origin,
            destination=constraints.destination,
            departure_date=departure_date,
            return_date=return_date,
            price=price,
            currency=currency,
            direct=direct,
            duration_minutes=duration_minutes,
        )

    @staticmethod
    def _parse_date(value: Optional[str]) -> Optional[date]:
        """Extract a date from an ISO datetime string."""

        if not value:
            return None

        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None

    @staticmethod
    def _duration_minutes(slice_data: dict) -> Optional[int]:
        """Convert an ISO-8601 duration such as PT8H30M to minutes."""

        duration = slice_data.get("duration")

        if not duration or not duration.startswith("PT"):
            return None

        duration = duration[2:]

        hours = 0
        minutes = 0

        if "H" in duration:
            hours_text, duration = duration.split("H", 1)
            try:
                hours = int(hours_text)
            except ValueError:
                return None

        if "M" in duration:
            minutes_text = duration.split("M", 1)[0]
            try:
                minutes = int(minutes_text)
            except ValueError:
                return None

        return hours * 60 + minutes

    @staticmethod
    def _return_date(
        constraints: TravelConstraints,
    ) -> Optional[date]:
        """Determine return date from explicit date or trip duration."""

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