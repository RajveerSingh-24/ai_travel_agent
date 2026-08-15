from datetime import date
from unittest.mock import Mock

import pytest

from schemas.travel import TravelConstraints
from services.providers.duffel_flight_provider import DuffelFlightProvider


def make_constraints(**overrides):
    values = {
        "origin": "Delhi",
        "destination": "Paris",
        "departure_date": date(2026, 9, 1),
        "return_date": date(2026, 9, 10),
        "travellers": 2,
        "currency": "USD",
        "direct_flight": None,
        "budget": None,
        "hotel_rating": None,
        "duration_days": None,
    }
    values.update(overrides)
    return TravelConstraints(**values)


def make_duffel_response():
    return {
        "data": {
            "offers": [
                {
                    "id": "off_001",
                    "total_amount": "850.00",
                    "total_currency": "USD",
                    "slices": [
                        {
                            "duration": "PT8H30M",
                            "segments": [
                                {
                                    "departing_at": "2026-09-01T10:00:00",
                                    "arriving_at": "2026-09-01T18:30:00",
                                    "operating_carrier": {
                                        "name": "Example Airlines"
                                    },
                                }
                            ],
                        },
                        {
                            "duration": "PT9H00M",
                            "segments": [
                                {
                                    "departing_at": "2026-09-10T12:00:00",
                                    "arriving_at": "2026-09-10T21:00:00",
                                    "operating_carrier": {
                                        "name": "Example Airlines"
                                    },
                                }
                            ],
                        },
                    ],
                }
            ]
        }
    }


def test_provider_implements_flight_provider():
    from services.providers.flight_provider import FlightProvider

    provider = DuffelFlightProvider(api_client=Mock())

    assert isinstance(provider, FlightProvider)


def test_provider_builds_round_trip_offer_request():
    api_client = Mock()
    api_client.post.return_value.json.return_value = make_duffel_response()

    provider = DuffelFlightProvider(
        api_client=api_client,
        location_service=Mock(
            resolve=Mock(side_effect=["DEL", "PAR"])
        ),
        api_token="test-token",
    )

    constraints = make_constraints()

    provider.search(constraints)

    api_client.post.assert_called_once()

    _, kwargs = api_client.post.call_args

    payload = kwargs["json"]

    assert len(payload["data"]["slices"]) == 2

    assert payload["data"]["slices"][0] == {
        "origin": "DEL",
        "destination": "PAR",
        "departure_date": "2026-09-01",
    }

    assert payload["data"]["slices"][1] == {
        "origin": "PAR",
        "destination": "DEL",
        "departure_date": "2026-09-10",
    }

    assert len(payload["data"]["passengers"]) == 2


def test_provider_maps_duffel_offer_to_flight_option():
    api_client = Mock()
    api_client.post.return_value.json.return_value = make_duffel_response()

    provider = DuffelFlightProvider(
        api_client=api_client,
        location_service=Mock(
            resolve=Mock(side_effect=["DEL", "PAR"])
        ),
        api_token="test-token",
    )

    results = provider.search(make_constraints())

    assert len(results) == 1

    flight = results[0]

    assert flight.id == "off_001"
    assert flight.airline == "Example Airlines"
    assert flight.origin == "Delhi"
    assert flight.destination == "Paris"
    assert flight.departure_date == date(2026, 9, 1)
    assert flight.return_date == date(2026, 9, 10)
    assert flight.price == 850.0
    assert flight.currency == "USD"
    assert flight.direct is True


def test_direct_flight_constraint_sets_zero_max_connections():
    api_client = Mock()
    api_client.post.return_value.json.return_value = make_duffel_response()

    provider = DuffelFlightProvider(
        api_client=api_client,
        location_service=Mock(
            resolve=Mock(side_effect=["DEL", "PAR"])
        ),
        api_token="test-token",
    )

    provider.search(
        make_constraints(direct_flight=True)
    )

    _, kwargs = api_client.post.call_args

    assert kwargs["json"]["data"]["max_connections"] == 0


def test_budget_filters_expensive_offers():
    api_client = Mock()
    api_client.post.return_value.json.return_value = make_duffel_response()

    provider = DuffelFlightProvider(
        api_client=api_client,
        location_service=Mock(
            resolve=Mock(side_effect=["DEL", "PAR"])
        ),
        api_token="test-token",
    )

    results = provider.search(
        make_constraints(budget=500)
    )

    assert results == []


def test_missing_required_constraints_returns_empty_list():
    provider = DuffelFlightProvider(
        api_client=Mock(),
        location_service=Mock(),
    )

    constraints = make_constraints(
        origin=None,
        destination=None,
        departure_date=None,
        return_date=None,
    )

    assert provider.search(constraints) == []