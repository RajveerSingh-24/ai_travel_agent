import main

from services.providers.duffel_flight_provider import DuffelFlightProvider
from services.providers.duffel_hotel_provider import DuffelHotelProvider
from services.providers.mock_flight_provider import MockFlightProvider
from services.providers.mock_hotel_provider import MockHotelProvider


def test_uses_mock_providers_by_default(monkeypatch):
    monkeypatch.delenv("USE_DUFFEL", raising=False)
    monkeypatch.delenv("USE_DUFFEL_HOTELS", raising=False)

    service = main.create_travel_search_service()

    assert isinstance(service.flight_provider, MockFlightProvider)
    assert isinstance(service.hotel_provider, MockHotelProvider)


def test_uses_duffel_flights_when_enabled(monkeypatch):
    monkeypatch.setenv("USE_DUFFEL", "true")
    monkeypatch.delenv("USE_DUFFEL_HOTELS", raising=False)

    service = main.create_travel_search_service()

    assert isinstance(service.flight_provider, DuffelFlightProvider)
    assert isinstance(service.hotel_provider, MockHotelProvider)


def test_uses_duffel_hotels_when_enabled(monkeypatch):
    monkeypatch.delenv("USE_DUFFEL", raising=False)
    monkeypatch.setenv("USE_DUFFEL_HOTELS", "true")

    service = main.create_travel_search_service()

    assert isinstance(service.flight_provider, MockFlightProvider)
    assert isinstance(service.hotel_provider, DuffelHotelProvider)


def test_uses_duffel_for_both_when_both_are_enabled(monkeypatch):
    monkeypatch.setenv("USE_DUFFEL", "true")
    monkeypatch.setenv("USE_DUFFEL_HOTELS", "true")

    service = main.create_travel_search_service()

    assert isinstance(service.flight_provider, DuffelFlightProvider)
    assert isinstance(service.hotel_provider, DuffelHotelProvider)