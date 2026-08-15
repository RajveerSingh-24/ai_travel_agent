from datetime import date
from unittest.mock import patch
import pytest

from schemas.travel import TravelConstraints
from services.langgraph_orchestrator import LangGraphTravelOrchestrator


@pytest.fixture
def mock_llm_service():
    """Replace the Gemini-backed LLM service with a local mock."""
    with patch("services.langgraph_orchestrator.LLMService") as mock_service_class:
        yield mock_service_class.return_value


class TestLangGraphTravelOrchestrator:
    """Tests for LangGraphTravelOrchestrator."""

    def test_incomplete_constraints_return_missing_fields_and_clarification(self, mock_llm_service):
        mock_llm_service.parse_travel_request.return_value = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date=date(2026, 9, 1),
            travellers=2,
        )
        orchestrator = LangGraphTravelOrchestrator()

        # Invoke orchestrator
        state = orchestrator.process_message(
            session_id="session-1",
            user_message="I want to visit Paris",
        )

        # Check assertions
        assert state["session_id"] == "session-1"
        assert state["validation"].is_complete is False
        assert state["validation"].missing_fields == ["return_date or duration_days"]
        assert state["clarification_message"] == "How many days would you like to stay?"
        assert state["recommendations"] is None

    def test_complete_constraints_run_search_and_recommendations(self, mock_llm_service):
        mock_llm_service.parse_travel_request.return_value = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date=date(2026, 9, 1),
            return_date=date(2026, 9, 15),
            travellers=2,
        )
        orchestrator = LangGraphTravelOrchestrator()

        # Invoke orchestrator
        state = orchestrator.process_message(
            session_id="session-2",
            user_message="Plan a trip to Paris from Sept 1 to Sept 15",
        )

        # Check assertions
        assert state["session_id"] == "session-2"
        assert state["validation"].is_complete is True
        assert state["validation"].missing_fields == []
        assert state["clarification_message"] is None
        assert state["recommendations"] is not None
        assert len(state["recommendations"]) == 3
        # First option should be the best option
        assert state["recommendations"][0].flight is not None
        assert state["recommendations"][0].hotel is not None

    def test_existing_and_new_constraints_are_merged(self, mock_llm_service):
        existing = TravelConstraints(origin="New York", travellers=2)
        mock_llm_service.parse_travel_request.return_value = TravelConstraints(
            destination="Paris",
            departure_date=date(2026, 9, 1),
            duration_days=7,
        )
        orchestrator = LangGraphTravelOrchestrator()

        # Invoke orchestrator with existing constraints
        state = orchestrator.process_message(
            session_id="session-3",
            user_message="Paris for a week on September 1",
            existing_constraints=existing,
        )

        assert state["constraints"].origin == "New York"
        assert state["constraints"].destination == "Paris"
        assert state["constraints"].departure_date == date(2026, 9, 1)
        assert state["constraints"].duration_days == 7
        assert state["constraints"].travellers == 2
        assert state["validation"].is_complete is True
        assert state["recommendations"] is not None

    def test_recommendations_under_budget_are_filtered(self, mock_llm_service):
        # Setting a low budget to ensure we filter out expensive recommendations if any
        mock_llm_service.parse_travel_request.return_value = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date=date(2026, 9, 1),
            duration_days=7,
            travellers=2,
            budget=1500.0,
        )
        orchestrator = LangGraphTravelOrchestrator()

        state = orchestrator.process_message(
            session_id="session-4",
            user_message="Plan a budget trip under $1500",
        )

        assert state["validation"].is_complete is True
        assert state["recommendations"] is not None
        for rec in state["recommendations"]:
            assert rec.total_price <= 1500.0
