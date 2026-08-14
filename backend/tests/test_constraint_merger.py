import pytest
from datetime import date
from schemas.travel import TravelConstraints
from services.constraint_merger import merge_travel_constraints


class TestMergeTravelConstraints:
    """Tests for merge_travel_constraints function."""

    def test_new_values_fill_missing_existing(self):
        """Test that new non-None values fill missing values in existing constraints."""
        existing = TravelConstraints(
            origin="New York",
            destination=None,
            departure_date=None,
            return_date=None,
            duration_days=None,
            travellers=None,
            budget=None,
            currency=None,
            direct_flight=None,
            hotel_rating=None,
        )

        new = TravelConstraints(
            origin=None,
            destination="Paris",
            departure_date=date(2026, 9, 1),
            return_date=date(2026, 9, 15),
            duration_days=14,
            travellers=2,
            budget=5000.0,
            currency="USD",
            direct_flight=True,
            hotel_rating=4.0,
        )

        merged = merge_travel_constraints(existing, new)

        assert merged.origin == "New York"  # From existing
        assert merged.destination == "Paris"  # From new
        assert merged.departure_date == date(2026, 9, 1)  # From new
        assert merged.return_date == date(2026, 9, 15)  # From new
        assert merged.duration_days == 14  # From new
        assert merged.travellers == 2  # From new
        assert merged.budget == 5000.0  # From new
        assert merged.currency == "USD"  # From new
        assert merged.direct_flight is True  # From new
        assert merged.hotel_rating == 4.0  # From new

    def test_existing_values_preserved_when_new_none(self):
        """Test that existing values are preserved when new values are None."""
        existing = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date=date(2026, 9, 1),
            return_date=date(2026, 9, 15),
            duration_days=14,
            travellers=2,
            budget=5000.0,
            currency="USD",
            direct_flight=True,
            hotel_rating=4.0,
        )

        new = TravelConstraints(
            origin=None,
            destination=None,
            departure_date=None,
            return_date=None,
            duration_days=None,
            travellers=None,
            budget=None,
            currency=None,
            direct_flight=None,
            hotel_rating=None,
        )

        merged = merge_travel_constraints(existing, new)

        assert merged.origin == "New York"
        assert merged.destination == "Paris"
        assert merged.departure_date == date(2026, 9, 1)
        assert merged.return_date == date(2026, 9, 15)
        assert merged.duration_days == 14
        assert merged.travellers == 2
        assert merged.budget == 5000.0
        assert merged.currency == "USD"
        assert merged.direct_flight is True
        assert merged.hotel_rating == 4.0

    def test_new_values_override_existing(self):
        """Test that explicit new values override existing values."""
        existing = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date=date(2026, 9, 1),
            return_date=date(2026, 9, 15),
            duration_days=14,
            travellers=2,
            budget=5000.0,
            currency="USD",
            direct_flight=True,
            hotel_rating=4.0,
        )

        new = TravelConstraints(
            origin="Los Angeles",
            destination="Tokyo",
            departure_date=date(2026, 10, 1),
            return_date=date(2026, 10, 20),
            duration_days=19,
            travellers=3,
            budget=8000.0,
            currency="EUR",
            direct_flight=False,
            hotel_rating=5.0,
        )

        merged = merge_travel_constraints(existing, new)

        assert merged.origin == "Los Angeles"
        assert merged.destination == "Tokyo"
        assert merged.departure_date == date(2026, 10, 1)
        assert merged.return_date == date(2026, 10, 20)
        assert merged.duration_days == 19
        assert merged.travellers == 3
        assert merged.budget == 8000.0
        assert merged.currency == "EUR"
        assert merged.direct_flight is False
        assert merged.hotel_rating == 5.0

    def test_mixed_merge_all_fields(self):
        """Test that all TravelConstraints fields are merged correctly in mixed scenario."""
        existing = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date=date(2026, 9, 1),
            return_date=None,
            duration_days=None,
            travellers=2,
            budget=None,
            currency="USD",
            direct_flight=False,
            hotel_rating=None,
        )

        new = TravelConstraints(
            origin=None,  # Keep existing
            destination=None,  # Keep existing
            departure_date=None,  # Keep existing
            return_date=date(2026, 9, 15),  # New
            duration_days=14,  # New
            travellers=None,  # Keep existing
            budget=5000.0,  # New
            currency=None,  # Keep existing
            direct_flight=True,  # Override existing
            hotel_rating=4.0,  # New
        )

        merged = merge_travel_constraints(existing, new)

        assert merged.origin == "New York"
        assert merged.destination == "Paris"
        assert merged.departure_date == date(2026, 9, 1)
        assert merged.return_date == date(2026, 9, 15)
        assert merged.duration_days == 14
        assert merged.travellers == 2
        assert merged.budget == 5000.0
        assert merged.currency == "USD"
        assert merged.direct_flight is True
        assert merged.hotel_rating == 4.0

    def test_existing_not_mutated(self):
        """Test that the existing TravelConstraints is not mutated."""
        existing = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date="2026-09-01",
            travellers=2,
        )

        new = TravelConstraints(
            origin="Los Angeles",
            destination="Tokyo",
            budget=5000.0,
        )

        # Store original values
        original_origin = existing.origin
        original_destination = existing.destination
        original_departure_date = existing.departure_date
        original_travellers = existing.travellers

        # Merge
        merged = merge_travel_constraints(existing, new)

        # Verify existing is unchanged
        assert existing.origin == original_origin
        assert existing.destination == original_destination
        assert existing.departure_date == original_departure_date
        assert existing.travellers == original_travellers

    def test_new_not_mutated(self):
        """Test that the new TravelConstraints is not mutated."""
        existing = TravelConstraints(
            origin="New York",
            destination="Paris",
            travellers=2,
        )

        new = TravelConstraints(
            origin="Los Angeles",
            destination="Tokyo",
            budget=5000.0,
        )

        # Store original values
        original_new_origin = new.origin
        original_new_destination = new.destination
        original_new_budget = new.budget

        # Merge
        merged = merge_travel_constraints(existing, new)

        # Verify new is unchanged
        assert new.origin == original_new_origin
        assert new.destination == original_new_destination
        assert new.budget == original_new_budget

    def test_merged_is_new_object(self):
        """Test that merged result is a new object distinct from inputs."""
        existing = TravelConstraints(origin="New York")
        new = TravelConstraints(destination="Paris")

        merged = merge_travel_constraints(existing, new)

        # Verify merged is a different object
        assert merged is not existing
        assert merged is not new

    def test_empty_existing_with_populated_new(self):
        """Test merging empty existing constraints with populated new constraints."""
        existing = TravelConstraints()  # All fields None

        new = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date=date(2026, 9, 1),
            return_date=date(2026, 9, 15),
            duration_days=14,
            travellers=2,
            budget=5000.0,
            currency="USD",
            direct_flight=True,
            hotel_rating=4.0,
        )

        merged = merge_travel_constraints(existing, new)

        assert merged.origin == "New York"
        assert merged.destination == "Paris"
        assert merged.departure_date == date(2026, 9, 1)
        assert merged.return_date == date(2026, 9, 15)
        assert merged.duration_days == 14
        assert merged.travellers == 2
        assert merged.budget == 5000.0
        assert merged.currency == "USD"
        assert merged.direct_flight is True
        assert merged.hotel_rating == 4.0

    def test_populated_existing_with_empty_new(self):
        """Test merging populated existing constraints with empty new constraints."""
        existing = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date=date(2026, 9, 1),
            return_date=date(2026, 9, 15),
            duration_days=14,
            travellers=2,
            budget=5000.0,
            currency="USD",
            direct_flight=True,
            hotel_rating=4.0,
        )

        new = TravelConstraints()  # All fields None

        merged = merge_travel_constraints(existing, new)

        assert merged.origin == "New York"
        assert merged.destination == "Paris"
        assert merged.departure_date == date(2026, 9, 1)
        assert merged.return_date == date(2026, 9, 15)
        assert merged.duration_days == 14
        assert merged.travellers == 2
        assert merged.budget == 5000.0
        assert merged.currency == "USD"
        assert merged.direct_flight is True
        assert merged.hotel_rating == 4.0

    def test_boolean_field_false_treated_as_explicit_value(self):
        """Test that False values for boolean fields are treated as explicit values."""
        existing = TravelConstraints(
            origin="New York",
            destination="Paris",
            direct_flight=True,  # Existing value is True
        )

        new = TravelConstraints(
            direct_flight=False,  # Explicitly setting to False
        )

        merged = merge_travel_constraints(existing, new)

        # False should override True (explicit value wins)
        assert merged.direct_flight is False
