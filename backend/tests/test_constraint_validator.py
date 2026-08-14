import pytest
from schemas.travel import TravelConstraints
from services.constraint_validator import validate_travel_constraints


class TestValidateTravelConstraints:
    """Tests for validate_travel_constraints function."""

    def test_complete_constraints(self):
        """Test that complete constraints return is_complete=True with no missing fields."""
        constraints = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date="2026-09-01",
            return_date="2026-09-15",
            duration_days=14,
            travellers=2,
            budget=5000.0,
            currency="USD",
            direct_flight=True,
            hotel_rating=4.0,
        )

        result = validate_travel_constraints(constraints)

        assert result.is_complete is True
        assert result.missing_fields == []

    def test_missing_origin(self):
        """Test that missing origin is reported."""
        constraints = TravelConstraints(
            origin=None,
            destination="Paris",
            departure_date="2026-09-01",
            return_date="2026-09-15",
            travellers=2,
        )

        result = validate_travel_constraints(constraints)

        assert result.is_complete is False
        assert "origin" in result.missing_fields

    def test_missing_destination(self):
        """Test that missing destination is reported."""
        constraints = TravelConstraints(
            origin="New York",
            destination=None,
            departure_date="2026-09-01",
            return_date="2026-09-15",
            travellers=2,
        )

        result = validate_travel_constraints(constraints)

        assert result.is_complete is False
        assert "destination" in result.missing_fields

    def test_missing_departure_date(self):
        """Test that missing departure date is reported."""
        constraints = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date=None,
            return_date="2026-09-15",
            travellers=2,
        )

        result = validate_travel_constraints(constraints)

        assert result.is_complete is False
        assert "departure_date" in result.missing_fields

    def test_missing_travellers(self):
        """Test that missing travellers is reported."""
        constraints = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date="2026-09-01",
            return_date="2026-09-15",
            travellers=None,
        )

        result = validate_travel_constraints(constraints)

        assert result.is_complete is False
        assert "travellers" in result.missing_fields

    def test_missing_return_date_and_duration_days(self):
        """Test that missing both return_date and duration_days is reported."""
        constraints = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date="2026-09-01",
            return_date=None,
            duration_days=None,
            travellers=2,
        )

        result = validate_travel_constraints(constraints)

        assert result.is_complete is False
        assert "return_date or duration_days" in result.missing_fields

    def test_return_date_provided(self):
        """Test that providing return_date satisfies round trip requirement."""
        constraints = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date="2026-09-01",
            return_date="2026-09-15",
            duration_days=None,
            travellers=2,
        )

        result = validate_travel_constraints(constraints)

        assert result.is_complete is True
        assert "return_date or duration_days" not in result.missing_fields

    def test_duration_days_provided(self):
        """Test that providing duration_days satisfies round trip requirement."""
        constraints = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date="2026-09-01",
            return_date=None,
            duration_days=14,
            travellers=2,
        )

        result = validate_travel_constraints(constraints)

        assert result.is_complete is True
        assert "return_date or duration_days" not in result.missing_fields

    def test_multiple_missing_fields(self):
        """Test that all expected missing fields are reported."""
        constraints = TravelConstraints(
            origin=None,
            destination=None,
            departure_date=None,
            return_date=None,
            duration_days=None,
            travellers=None,
        )

        result = validate_travel_constraints(constraints)

        assert result.is_complete is False
        assert len(result.missing_fields) == 5
        assert "origin" in result.missing_fields
        assert "destination" in result.missing_fields
        assert "departure_date" in result.missing_fields
        assert "travellers" in result.missing_fields
        assert "return_date or duration_days" in result.missing_fields

    def test_optional_fields_not_required(self):
        """Test that optional fields (budget, currency, etc.) are not required."""
        constraints = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date="2026-09-01",
            return_date="2026-09-15",
            travellers=2,
            budget=None,
            currency=None,
            direct_flight=None,
            hotel_rating=None,
        )

        result = validate_travel_constraints(constraints)

        assert result.is_complete is True
        assert result.missing_fields == []

    def test_to_dict(self):
        """Test ValidationResult.to_dict() method."""
        constraints = TravelConstraints(
            origin=None,
            destination="Paris",
            departure_date="2026-09-01",
            return_date="2026-09-15",
            travellers=2,
        )

        result = validate_travel_constraints(constraints)
        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert "is_complete" in result_dict
        assert "missing_fields" in result_dict
        assert result_dict["is_complete"] is False
        assert "origin" in result_dict["missing_fields"]
