from datetime import date

import pytest
from pydantic import ValidationError

from schemas.search import FlightOption, HotelOption


class TestFlightOption:
    """Tests for the provider-independent flight result model."""

    def test_valid_flight_option(self):
        option = FlightOption(
            id="flight-123",
            airline="Example Air",
            origin="New York",
            destination="Paris",
            departure_date="2026-09-01",
            return_date="2026-09-15",
            price=850.0,
            currency="USD",
            direct=True,
            duration_minutes=435,
        )

        assert option.departure_date == date(2026, 9, 1)
        assert option.return_date == date(2026, 9, 15)
        assert option.direct is True

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("id", ""),
            ("price", 0),
            ("currency", "US"),
            ("duration_minutes", 0),
        ],
    )
    def test_rejects_invalid_field_values(self, field, value):
        values = {
            "id": "flight-123",
            "airline": "Example Air",
            "origin": "New York",
            "destination": "Paris",
            "departure_date": "2026-09-01",
            "return_date": "2026-09-15",
            "price": 850.0,
            "currency": "USD",
            "direct": True,
            "duration_minutes": 435,
        }
        values[field] = value

        with pytest.raises(ValidationError):
            FlightOption(**values)

    def test_rejects_return_date_before_departure_date(self):
        with pytest.raises(ValidationError, match="return_date cannot be before"):
            FlightOption(
                id="flight-123",
                airline="Example Air",
                origin="New York",
                destination="Paris",
                departure_date="2026-09-15",
                return_date="2026-09-01",
                price=850.0,
                currency="USD",
                direct=True,
                duration_minutes=435,
            )


class TestHotelOption:
    """Tests for the provider-independent hotel result model."""

    def test_valid_hotel_option(self):
        option = HotelOption(
            id="hotel-123",
            name="Example Hotel",
            destination="Paris",
            rating=4.5,
            price_per_night=180.0,
            total_price=1260.0,
            currency="USD",
        )

        assert option.name == "Example Hotel"
        assert option.rating == 4.5

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("id", ""),
            ("rating", 5.5),
            ("price_per_night", 0),
            ("total_price", -1),
            ("currency", "US"),
        ],
    )
    def test_rejects_invalid_field_values(self, field, value):
        values = {
            "id": "hotel-123",
            "name": "Example Hotel",
            "destination": "Paris",
            "rating": 4.5,
            "price_per_night": 180.0,
            "total_price": 1260.0,
            "currency": "USD",
        }
        values[field] = value

        with pytest.raises(ValidationError):
            HotelOption(**values)
