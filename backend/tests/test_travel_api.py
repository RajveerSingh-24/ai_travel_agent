import importlib
from unittest.mock import Mock, patch
from urllib import response

import httpx
import pytest
from fastapi.testclient import TestClient

from schemas.booking import BookingResult, BookingStatus
from schemas.travel import TravelConstraints
from services.search_service import TravelSearchResult


@pytest.fixture
def client_and_llm_service(monkeypatch):
    """Provide the API client with its Gemini-backed LLM service mocked."""
    original_client_init = httpx.Client.__init__

    def compatible_client_init(self, *args, **kwargs):
        kwargs.pop("app", None)
        original_client_init(self, *args, **kwargs)

    monkeypatch.setattr(httpx.Client, "__init__", compatible_client_init)

    import main
    main = importlib.reload(main)

    mock_llm_service = Mock()

    main.llm_service = mock_llm_service

    main.langgraph_orchestrator = main.LangGraphTravelOrchestrator(
        llm_service=mock_llm_service,
        search_service=main.travel_search_service,
        recommendation_service=main.travel_recommendation_service,
    )

    main.session_constraints.clear()
    main.session_recommendations.clear()

    with TestClient(main.app) as client:
        yield client, mock_llm_service, main
    



class TestTravelPlanEndpoint:
    """Tests for the session-aware travel planning endpoint."""

    def test_returns_complete_structured_plan(self, client_and_llm_service):
        client, mock_llm_service, _ = client_and_llm_service
        mock_llm_service.parse_travel_request.return_value = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date="2026-09-01",
            return_date="2026-09-15",
            travellers=2,
        )

        response = client.post(
            "/api/travel/plan",
            json={"session_id": "session-1", "message": "Plan a Paris trip"},
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["session_id"] == "session-1"
        assert response_data["is_complete"] is True
        assert response_data["missing_fields"] == []
        assert response_data["clarification_message"] is None
        assert len(response_data["recommendations"]) == 3
        assert response_data["pending_approval"] is None
        mock_llm_service.parse_travel_request.assert_called_once_with("Plan a Paris trip")

    def test_retains_and_merges_constraints_for_a_session(self, client_and_llm_service):
        client, mock_llm_service, _ = client_and_llm_service
        mock_llm_service.parse_travel_request.side_effect = [
            TravelConstraints(origin="New York", travellers=2),
            TravelConstraints(
                destination="Paris",
                departure_date="2026-09-01",
                duration_days=7,
            ),
        ]

        first_response = client.post(
            "/api/travel/plan",
            json={"session_id": "session-2", "message": "Leaving New York with two people"},
        )
        second_response = client.post(
            "/api/travel/plan",
            json={"session_id": "session-2", "message": "Paris on September 1 for a week"},
        )

        assert first_response.status_code == 200
        assert first_response.json()["is_complete"] is False
        assert first_response.json()["recommendations"] is None
        assert second_response.status_code == 200
        assert second_response.json()["constraints"]["origin"] == "New York"
        assert second_response.json()["constraints"]["destination"] == "Paris"
        assert second_response.json()["constraints"]["travellers"] == 2
        assert second_response.json()["is_complete"] is True
        assert second_response.json()["clarification_message"] is None
        assert len(second_response.json()["recommendations"]) == 3

    def test_rejects_empty_message(self, client_and_llm_service):
        client, mock_llm_service, _ = client_and_llm_service

        response = client.post(
            "/api/travel/plan",
            json={"session_id": "session-3", "message": ""},
        )

        assert response.status_code == 422
        mock_llm_service.parse_travel_request.assert_not_called()

    def test_returns_bad_request_for_invalid_llm_input(self, client_and_llm_service):
        client, mock_llm_service, _ = client_and_llm_service
        mock_llm_service.parse_travel_request.side_effect = ValueError(
            "User message cannot be empty"
        )

        response = client.post(
            "/api/travel/plan",
            json={"session_id": "session-4", "message": "Invalid request"},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "User message cannot be empty"

    def test_filters_recommendations_by_budget(self, client_and_llm_service):
        client, mock_llm_service, _ = client_and_llm_service
        mock_llm_service.parse_travel_request.return_value = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date="2026-09-01",
            duration_days=7,
            travellers=2,
            budget=1500.0,
        )

        response = client.post(
            "/api/travel/plan",
            json={"session_id": "session-5", "message": "Plan a budget trip"},
        )

        assert response.status_code == 200
        recommendations = response.json()["recommendations"]
        assert recommendations
        assert all(
            recommendation["total_price"] <= 1500.0
            for recommendation in recommendations
        )

    def test_returns_empty_recommendations_when_search_has_no_results(
        self, client_and_llm_service
    ):
        client, mock_llm_service, main = client_and_llm_service
        mock_llm_service.parse_travel_request.return_value = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date="2026-09-01",
            return_date="2026-09-08",
            travellers=2,
        )
        main.langgraph_orchestrator._search_service = Mock()
        main.langgraph_orchestrator._search_service.search.return_value = TravelSearchResult(
            flights=[],
            hotels=[],
        )

        response = client.post(
            "/api/travel/plan",
            json={"session_id": "session-6", "message": "Plan my trip"},
        )

        assert response.status_code == 200
        assert response.json()["is_complete"] is True
        assert response.json()["recommendations"] == []


class TestTravelApprovalEndpoint:
    """Tests for resolving in-memory travel recommendation approvals."""

    def test_approves_valid_pending_approval(self, client_and_llm_service):
        client, _, main = client_and_llm_service
        pending = main.travel_approval_service.create_pending_approval(
            "session-1",
            ["flight-1", "hotel-1"],
        )

        response = client.post(
            "/api/travel/approval",
            json={
                "session_id": "session-1",
                "approval_id": pending.approval_id,
                "action": "approve",
            },
        )

        assert response.status_code == 200
        assert response.json()["approval"]["status"] == "approved"

    def test_rejects_valid_pending_approval(self, client_and_llm_service):
        client, _, main = client_and_llm_service
        pending = main.travel_approval_service.create_pending_approval(
            "session-1",
            ["flight-1", "hotel-1"],
        )

        response = client.post(
            "/api/travel/approval",
            json={
                "session_id": "session-1",
                "approval_id": pending.approval_id,
                "action": "reject",
            },
        )

        assert response.status_code == 200
        assert response.json()["approval"]["status"] == "rejected"

    def test_returns_not_found_for_unknown_approval(self, client_and_llm_service):
        client, _, _ = client_and_llm_service

        response = client.post(
            "/api/travel/approval",
            json={
                "session_id": "session-1",
                "approval_id": "missing-approval",
                "action": "approve",
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Unknown approval ID"

    def test_returns_forbidden_for_wrong_session(self, client_and_llm_service):
        client, _, main = client_and_llm_service
        pending = main.travel_approval_service.create_pending_approval(
            "session-1",
            ["flight-1", "hotel-1"],
        )

        response = client.post(
            "/api/travel/approval",
            json={
                "session_id": "session-2",
                "approval_id": pending.approval_id,
                "action": "approve",
            },
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Approval does not belong to this session"

    def test_returns_conflict_for_already_resolved_approval(
        self, client_and_llm_service
    ):
        client, _, main = client_and_llm_service
        pending = main.travel_approval_service.create_pending_approval(
            "session-1",
            ["flight-1", "hotel-1"],
        )
        main.travel_approval_service.approve("session-1", pending.approval_id)

        response = client.post(
            "/api/travel/approval",
            json={
                "session_id": "session-1",
                "approval_id": pending.approval_id,
                "action": "reject",
            },
        )

        assert response.status_code == 409
        assert response.json()["detail"] == "Approval has already been resolved"

    def test_completed_plan_creates_pending_approval_for_selected_recommendation(
        self, client_and_llm_service
    ):
        client, mock_llm_service, _ = client_and_llm_service
        mock_llm_service.parse_travel_request.return_value = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date="2026-09-01",
            return_date="2026-09-08",
            travellers=2,
        )

        response = client.post(
            "/api/travel/plan",
            json={
                "session_id": "session-7",
                "message": "Plan my trip",
                "selected_recommendation_ids": [
                    "mock-flight-001",
                    "mock-hotel-001",
                ],
            },
        )

        assert response.status_code == 200
        approval = response.json()["pending_approval"]
        assert approval["session_id"] == "session-7"
        assert approval["selected_recommendation_ids"] == [
            "mock-flight-001",
            "mock-hotel-001",
        ]
        assert approval["status"] == "pending"


class TestTravelBookingEndpoint:
    """Tests for booking approved in-memory travel recommendations."""

    @staticmethod
    def create_pending_approval(
        client,
        mock_llm_service,
        selected_recommendation_ids=None,
    ):
        if selected_recommendation_ids is None:
            selected_recommendation_ids = [
                "mock-flight-001",
                "mock-hotel-001",
            ]
        mock_llm_service.parse_travel_request.return_value = TravelConstraints(
            origin="New York",
            destination="Paris",
            departure_date="2026-09-01",
            return_date="2026-09-08",
            travellers=2,
        )
        response = client.post(
            "/api/travel/plan",
            json={
                "session_id": "booking-session",
                "message": "Plan my trip",
                "selected_recommendation_ids": selected_recommendation_ids,
            },
        )
        assert response.status_code == 200
        return response.json()["pending_approval"]["approval_id"]

    @staticmethod
    def approve(client, approval_id):
        response = client.post(
            "/api/travel/approval",
            json={
                "session_id": "booking-session",
                "approval_id": approval_id,
                "action": "approve",
            },
        )
        assert response.status_code == 200

    def test_books_an_approved_recommendation(self, client_and_llm_service):
        client, mock_llm_service, _ = client_and_llm_service
        approval_id = self.create_pending_approval(client, mock_llm_service)
        self.approve(client, approval_id)

        response = client.post(
            "/api/travel/book",
            json={"session_id": "booking-session", "approval_id": approval_id},
        )

        assert response.status_code == 200
        assert response.json()["booking"]["status"] == "confirmed"
        assert response.json()["booking"]["selected_flight_id"] == "mock-flight-001"
        assert response.json()["booking"]["selected_hotel_id"] == "mock-hotel-001"

    def test_rejects_booking_for_pending_approval(self, client_and_llm_service):
        client, mock_llm_service, _ = client_and_llm_service
        approval_id = self.create_pending_approval(client, mock_llm_service)

        response = client.post(
            "/api/travel/book",
            json={"session_id": "booking-session", "approval_id": approval_id},
        )

        assert response.status_code == 409
        assert response.json()["detail"] == "Approval is still pending"

    def test_rejects_booking_for_rejected_approval(self, client_and_llm_service):
        client, mock_llm_service, _ = client_and_llm_service
        approval_id = self.create_pending_approval(client, mock_llm_service)
        response = client.post(
            "/api/travel/approval",
            json={
                "session_id": "booking-session",
                "approval_id": approval_id,
                "action": "reject",
            },
        )
        assert response.status_code == 200

        response = client.post(
            "/api/travel/book",
            json={"session_id": "booking-session", "approval_id": approval_id},
        )

        assert response.status_code == 409
        assert response.json()["detail"] == "Approval was rejected"

    def test_returns_not_found_for_unknown_booking_approval(
        self, client_and_llm_service
    ):
        client, _, _ = client_and_llm_service

        response = client.post(
            "/api/travel/book",
            json={"session_id": "booking-session", "approval_id": "missing"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Unknown approval ID"

    def test_returns_forbidden_for_booking_with_wrong_session(
        self, client_and_llm_service
    ):
        client, mock_llm_service, _ = client_and_llm_service
        approval_id = self.create_pending_approval(client, mock_llm_service)
        self.approve(client, approval_id)

        response = client.post(
            "/api/travel/book",
            json={"session_id": "other-session", "approval_id": approval_id},
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Approval does not belong to this session"

    def test_returns_provider_booking_failure(self, client_and_llm_service):
        client, mock_llm_service, main = client_and_llm_service
        approval_id = self.create_pending_approval(client, mock_llm_service)
        self.approve(client, approval_id)
        main.langgraph_orchestrator.graph.update_state(
            {"configurable": {"thread_id": "booking-session"}},
            {"constraints": main.langgraph_orchestrator.get_constraints("booking-session").model_copy(update={"budget": 1.0})},
        )

        response = client.post(
            "/api/travel/book",
            json={"session_id": "booking-session", "approval_id": approval_id},
        )

        assert response.status_code == 200
        assert response.json()["booking"]["status"] == "failed"

    def test_repeated_booking_returns_same_result_without_calling_provider_again(
        self, client_and_llm_service
    ):
        client, mock_llm_service, main = client_and_llm_service
        approval_id = self.create_pending_approval(client, mock_llm_service)
        self.approve(client, approval_id)
        provider = Mock()
        provider.book.return_value = BookingResult(
            booking_id="cached-booking-1",
            status=BookingStatus.CONFIRMED,
            selected_flight_id="mock-flight-001",
            selected_hotel_id="mock-hotel-001",
            total_price=1340.0,
            currency="USD",
        )
        main.booking_service.booking_provider = provider

        first_response = client.post(
            "/api/travel/book",
            json={"session_id": "booking-session", "approval_id": approval_id},
        )
        provider.reset_mock()
        second_response = client.post(
            "/api/travel/book",
            json={"session_id": "booking-session", "approval_id": approval_id},
        )

        assert first_response.status_code == 200
        assert second_response.status_code == 200
        assert second_response.json()["booking"] == first_response.json()["booking"]
        provider.book.assert_not_called()

    def test_failed_booking_is_returned_unchanged_on_repeat(self, client_and_llm_service):
        client, mock_llm_service, main = client_and_llm_service
        approval_id = self.create_pending_approval(client, mock_llm_service)
        self.approve(client, approval_id)
        main.langgraph_orchestrator.graph.update_state(
            {"configurable": {"thread_id": "booking-session"}},
            {"constraints": main.langgraph_orchestrator.get_constraints("booking-session").model_copy(update={"budget": 1.0})},
        )

        first_response = client.post(
            "/api/travel/book",
            json={"session_id": "booking-session", "approval_id": approval_id},
        )
        second_response = client.post(
            "/api/travel/book",
            json={"session_id": "booking-session", "approval_id": approval_id},
        )

        assert first_response.status_code == 200
        assert first_response.json()["booking"]["status"] == "failed"
        assert second_response.json()["booking"] == first_response.json()["booking"]

    def test_different_approvals_create_independent_bookings(
        self, client_and_llm_service
    ):
        client, mock_llm_service, main = client_and_llm_service
        provider = Mock()
        provider.book.side_effect = [
            BookingResult(
                booking_id="booking-1",
                status=BookingStatus.CONFIRMED,
                selected_flight_id="mock-flight-001",
                selected_hotel_id="mock-hotel-001",
                total_price=1340.0,
                currency="USD",
            ),
            BookingResult(
                booking_id="booking-2",
                status=BookingStatus.CONFIRMED,
                selected_flight_id="mock-flight-001",
                selected_hotel_id="mock-hotel-001",
                total_price=1340.0,
                currency="USD",
            ),
        ]
        main.booking_service.booking_provider = provider

        first_approval_id = self.create_pending_approval(client, mock_llm_service)
        self.approve(client, first_approval_id)
        second_approval_id = self.create_pending_approval(client, mock_llm_service)
        self.approve(client, second_approval_id)

        first_response = client.post(
            "/api/travel/book",
            json={
                "session_id": "booking-session",
                "approval_id": first_approval_id,
            },
        )
        second_response = client.post(
            "/api/travel/book",
            json={
                "session_id": "booking-session",
                "approval_id": second_approval_id,
            },
        )

        assert first_response.status_code == 200
        assert second_response.status_code == 200
        assert provider.book.call_count == 2
        assert first_response.json()["booking"]["booking_id"] == "booking-1"
        assert second_response.json()["booking"]["booking_id"] == "booking-2"
        assert (
            main.booking_service._bookings[first_approval_id]
            is not main.booking_service._bookings[second_approval_id]
        )
