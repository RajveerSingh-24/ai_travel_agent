import pytest
from services.constraint_validator import ValidationResult
from services.clarification_service import generate_clarification_message


class TestGenerateClarificationMessage:
    """Tests for generate_clarification_message function."""

    def test_complete_validation_result(self):
        """Test that complete validation returns the completion message."""
        result = ValidationResult(is_complete=True, missing_fields=[])

        message = generate_clarification_message(result)

        assert (
            message
            == "Great! I have all the information needed to help you plan your trip."
        )

    def test_single_missing_field_origin(self):
        """Test that missing only origin returns the origin question."""
        result = ValidationResult(is_complete=False, missing_fields=["origin"])

        message = generate_clarification_message(result)

        assert message == "What city will you be departing from?"

    def test_single_missing_field_destination(self):
        """Test that missing only destination returns the destination question."""
        result = ValidationResult(is_complete=False, missing_fields=["destination"])

        message = generate_clarification_message(result)

        assert message == "Where would you like to travel?"

    def test_single_missing_field_departure_date(self):
        """Test that missing only departure_date returns the departure date question."""
        result = ValidationResult(
            is_complete=False, missing_fields=["departure_date"]
        )

        message = generate_clarification_message(result)

        assert message == "What date would you like to depart?"

    def test_single_missing_field_travellers(self):
        """Test that missing only travellers returns the travellers question."""
        result = ValidationResult(is_complete=False, missing_fields=["travellers"])

        message = generate_clarification_message(result)

        assert message == "How many people will be travelling?"

    def test_single_missing_field_return_or_duration(self):
        """Test that missing return_date or duration_days returns the duration question."""
        result = ValidationResult(
            is_complete=False, missing_fields=["return_date or duration_days"]
        )

        message = generate_clarification_message(result)

        assert message == "How many days would you like to stay?"

    def test_multiple_missing_fields(self):
        """Test that multiple missing fields returns all questions in order."""
        result = ValidationResult(
            is_complete=False,
            missing_fields=[
                "origin",
                "destination",
                "travellers",
            ],
        )

        message = generate_clarification_message(result)

        assert "To help you plan your trip, I need to know:" in message
        assert "1. What city will you be departing from?" in message
        assert "2. Where would you like to travel?" in message
        assert "3. How many people will be travelling?" in message

    def test_multiple_fields_including_return_or_duration(self):
        """Test multiple missing fields including return_date or duration_days."""
        result = ValidationResult(
            is_complete=False,
            missing_fields=[
                "origin",
                "departure_date",
                "return_date or duration_days",
            ],
        )

        message = generate_clarification_message(result)

        assert "To help you plan your trip, I need to know:" in message
        assert "1. What city will you be departing from?" in message
        assert "2. What date would you like to depart?" in message
        assert "3. How many days would you like to stay?" in message

    def test_all_required_fields_missing(self):
        """Test that all required fields missing returns all questions."""
        result = ValidationResult(
            is_complete=False,
            missing_fields=[
                "origin",
                "destination",
                "departure_date",
                "travellers",
                "return_date or duration_days",
            ],
        )

        message = generate_clarification_message(result)

        assert "To help you plan your trip, I need to know:" in message
        assert "1. What city will you be departing from?" in message
        assert "2. Where would you like to travel?" in message
        assert "3. What date would you like to depart?" in message
        assert "4. How many people will be travelling?" in message
        assert "5. How many days would you like to stay?" in message

    def test_unknown_missing_field(self):
        """Test that an unknown missing field returns the fallback message."""
        result = ValidationResult(
            is_complete=False, missing_fields=["unknown_field"]
        )

        message = generate_clarification_message(result)

        assert message == "Please provide additional travel information to continue."

    def test_mixed_known_and_unknown_fields(self):
        """Test that a mix of known and unknown fields returns questions for known fields."""
        result = ValidationResult(
            is_complete=False,
            missing_fields=["origin", "unknown_field"],
        )

        message = generate_clarification_message(result)

        # Should still contain the known field question
        assert "What city will you be departing from?" in message

    def test_message_formatting_two_questions(self):
        """Test that message formatting is correct for two missing fields."""
        result = ValidationResult(
            is_complete=False,
            missing_fields=["origin", "destination"],
        )

        message = generate_clarification_message(result)

        lines = message.split("\n")
        assert len(lines) == 3  # Header + 2 questions
        assert lines[0] == "To help you plan your trip, I need to know:"
        assert lines[1] == "1. What city will you be departing from?"
        assert lines[2] == "2. Where would you like to travel?"
