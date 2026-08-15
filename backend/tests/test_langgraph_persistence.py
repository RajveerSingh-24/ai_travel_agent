from datetime import date
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from schemas.travel import TravelConstraints
from schemas.booking import BookingStatus
import main


@pytest.fixture
def client_with_mock_llm():
    """Fixture that patches LLMService inside main and orchestrator."""
    with patch("services.langgraph_orchestrator.LLMService") as mock_class:
        mock_llm = mock_class.return_value
        # Re-initialize main app to reload the orchestrator in the patch context
        import importlib
        importlib.reload(main)
        main.session_recommendations.clear()

        with TestClient(main.app) as client:
            yield client, mock_llm


class TestLangGraphConversationalState:
    """Validate multi-turn persistence, session isolation, and API integration."""

    def test_multiturn_conversational_flow_and_isolation(self, client_with_mock_llm):
        client, mock_llm = client_with_mock_llm

        # Step 1: Send first incomplete message for Session A
        # LangGraph parses constraints from user message and saves them.
        mock_llm.parse_travel_request.return_value = TravelConstraints(
            origin="New York",
            travellers=2
        )

        response_a1 = client.post(
            "/api/travel/plan",
            json={"session_id": "session-A", "message": "Leaving New York with two people"}
        )
        assert response_a1.status_code == 200
        data_a1 = response_a1.json()
        assert data_a1["is_complete"] is False
        assert data_a1["constraints"]["origin"] == "New York"
        assert data_a1["constraints"]["travellers"] == 2
        assert data_a1["recommendations"] is None
        assert data_a1["clarification_message"] is not None

        # Step 2: Send first incomplete message for Session B (isolation test)
        # Session B starts with its own constraints, unaffected by Session A
        mock_llm.parse_travel_request.return_value = TravelConstraints(
            origin="London",
            destination="Tokyo",
            travellers=1
        )

        response_b1 = client.post(
            "/api/travel/plan",
            json={"session_id": "session-B", "message": "London to Tokyo alone"}
        )
        assert response_b1.status_code == 200
        data_b1 = response_b1.json()
        assert data_b1["is_complete"] is False
        assert data_b1["constraints"]["origin"] == "London"
        assert data_b1["constraints"]["destination"] == "Tokyo"
        assert data_b1["constraints"]["travellers"] == 1

        # Step 3: Send second message for Session A to complete the constraints
        # It should load origin=New York, travellers=2 from MemorySaver,
        # merge with destination=Paris, departure_date=2026-09-01, return_date=2026-09-15,
        # and trigger search and recommendation.
        mock_llm.parse_travel_request.return_value = TravelConstraints(
            destination="Paris",
            departure_date=date(2026, 9, 1),
            return_date=date(2026, 9, 15),
        )

        response_a2 = client.post(
            "/api/travel/plan",
            json={"session_id": "session-A", "message": "Paris on Sept 1 to Sept 15"}
        )
        assert response_a2.status_code == 200
        data_a2 = response_a2.json()
        assert data_a2["is_complete"] is True
        assert data_a2["constraints"]["origin"] == "New York"
        assert data_a2["constraints"]["destination"] == "Paris"
        assert data_a2["constraints"]["travellers"] == 2
        assert data_a2["constraints"]["departure_date"] == "2026-09-01"
        assert data_a2["constraints"]["return_date"] == "2026-09-15"
        assert data_a2["clarification_message"] is None
        # Recommendations should appear now that it's complete
        assert data_a2["recommendations"] is not None
        assert len(data_a2["recommendations"]) == 3

        # Step 4: Verify Session B constraints remain unaffected (isolation test)
        # Send another query to Session B
        mock_llm.parse_travel_request.return_value = TravelConstraints(
            departure_date=date(2026, 10, 1),
        )
        response_b2 = client.post(
            "/api/travel/plan",
            json={"session_id": "session-B", "message": "Leaving on Oct 1"}
        )
        assert response_b2.status_code == 200
        data_b2 = response_b2.json()
        assert data_b2["constraints"]["origin"] == "London"
        assert data_b2["constraints"]["destination"] == "Tokyo"
        assert data_b2["constraints"]["departure_date"] == "2026-10-01"
        # Since Session B is still incomplete (no return_date or duration_days),
        # is_complete should be False and recommendations should be None.
        assert data_b2["is_complete"] is False
        assert data_b2["recommendations"] is None

    def test_existing_approval_and_booking_flows_are_intact(self, client_with_mock_llm):
        client, mock_llm = client_with_mock_llm

        # Step 1: Complete session plan
        mock_llm.parse_travel_request.return_value = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date=date(2026, 9, 1),
            return_date=date(2026, 9, 15),
            travellers=2,
        )

        response = client.post(
            "/api/travel/plan",
            json={"session_id": "session-C", "message": "Complete plan"}
        )
        data = response.json()
        assert data["is_complete"] is True
        recommendations = data["recommendations"]
        selected_rec = recommendations[0]
        selected_ids = [selected_rec["flight"]["id"], selected_rec["hotel"]["id"]]

        # Step 2: Select recommendation to create a pending approval
        response_sel = client.post(
            "/api/travel/plan",
            json={
                "session_id": "session-C",
                "message": "Select first option",
                "selected_recommendation_ids": selected_ids
            }
        )
        data_sel = response_sel.json()
        pending_approval = data_sel["pending_approval"]
        assert pending_approval is not None
        assert pending_approval["status"] == "pending"
        approval_id = pending_approval["approval_id"]

        # Step 3: Approve
        response_app = client.post(
            "/api/travel/approval",
            json={
                "session_id": "session-C",
                "approval_id": approval_id,
                "action": "approve"
            }
        )
        assert response_app.status_code == 200
        assert response_app.json()["approval"]["status"] == "approved"

        # Step 4: Book
        response_book = client.post(
            "/api/travel/book",
            json={
                "session_id": "session-C",
                "approval_id": approval_id
            }
        )
        assert response_book.status_code == 200
        booking_data = response_book.json()["booking"]
        assert booking_data["status"] in ("confirmed", BookingStatus.CONFIRMED)
        assert booking_data["selected_flight_id"] is not None
        assert booking_data["selected_hotel_id"] is not None
