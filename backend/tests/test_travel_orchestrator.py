from datetime import date
from unittest.mock import patch

import pytest

from schemas.travel import TravelConstraints
from services.travel_orchestrator import TravelOrchestrator


@pytest.fixture
def mock_llm_service():
    """Replace the Gemini-backed LLM service with a local mock."""
    with patch("services.travel_orchestrator.LLMService") as mock_service_class:
        yield mock_service_class.return_value


class TestTravelOrchestrator:
    """Tests for TravelOrchestrator.process_message()."""

    def test_complete_constraints_return_no_clarification(self, mock_llm_service):
        mock_llm_service.parse_travel_request.return_value = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date=date(2026, 9, 1),
            return_date=date(2026, 9, 15),
            travellers=2,
        )
        orchestrator = TravelOrchestrator()

        result = orchestrator.process_message("Plan a trip to Paris")

        mock_llm_service.parse_travel_request.assert_called_once_with(
            "Plan a trip to Paris"
        )
        assert result.validation.is_complete is True
        assert result.validation.missing_fields == []
        assert result.clarification_message is None

    def test_incomplete_constraints_return_missing_fields_and_clarification(
        self, mock_llm_service
    ):
        mock_llm_service.parse_travel_request.return_value = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date=date(2026, 9, 1),
            travellers=2,
        )
        orchestrator = TravelOrchestrator()

        result = orchestrator.process_message("I want to visit Paris")

        assert result.validation.is_complete is False
        assert result.validation.missing_fields == ["return_date or duration_days"]
        assert result.clarification_message == "How many days would you like to stay?"

    def test_existing_and_new_constraints_are_merged(self, mock_llm_service):
        existing = TravelConstraints(origin="New York", travellers=2)
        mock_llm_service.parse_travel_request.return_value = TravelConstraints(
            destination="Paris",
            departure_date=date(2026, 9, 1),
            duration_days=7,
        )
        orchestrator = TravelOrchestrator()

        result = orchestrator.process_message(
            "Paris for a week on September 1", existing
        )

        assert result.constraints.origin == "New York"
        assert result.constraints.destination == "Paris"
        assert result.constraints.departure_date == date(2026, 9, 1)
        assert result.constraints.duration_days == 7
        assert result.constraints.travellers == 2
        assert result.validation.is_complete is True

    def test_new_non_none_values_override_existing_values(self, mock_llm_service):
        existing = TravelConstraints(
            origin="New York",
            destination="Paris",
            travellers=2,
            direct_flight=True,
        )
        mock_llm_service.parse_travel_request.return_value = TravelConstraints(
            origin="Los Angeles",
            destination="Tokyo",
            travellers=3,
            direct_flight=False,
        )
        orchestrator = TravelOrchestrator()

        result = orchestrator.process_message("Change my trip", existing)

        assert result.constraints.origin == "Los Angeles"
        assert result.constraints.destination == "Tokyo"
        assert result.constraints.travellers == 3
        assert result.constraints.direct_flight is False

    def test_existing_constraints_are_not_mutated(self, mock_llm_service):
        existing = TravelConstraints(
            origin="New York",
            destination="Paris",
            travellers=2,
        )
        original_values = existing.model_dump()
        mock_llm_service.parse_travel_request.return_value = TravelConstraints(
            destination="Tokyo",
            duration_days=10,
        )
        orchestrator = TravelOrchestrator()

        result = orchestrator.process_message("Change destination", existing)

        assert existing.model_dump() == original_values
        assert result.constraints is not existing
        assert result.constraints.destination == "Tokyo"
        assert result.constraints.duration_days == 10
