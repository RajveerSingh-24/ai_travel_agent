import importlib
from unittest.mock import Mock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from schemas.travel import TravelConstraints
from services.search_service import TravelSearchResult


@pytest.fixture
def client_and_llm_service(monkeypatch):
    """Provide the API client with its Gemini-backed LLM service mocked."""
    original_client_init = httpx.Client.__init__

    def compatible_client_init(self, *args, **kwargs):
        """Support Starlette 0.27 passing its removed ``app`` argument."""
        kwargs.pop("app", None)
        original_client_init(self, *args, **kwargs)

    monkeypatch.setattr(httpx.Client, "__init__", compatible_client_init)

    with patch("services.travel_orchestrator.LLMService") as mock_llm_service_class:
        import main

        main = importlib.reload(main)
        main.session_constraints.clear()

        with TestClient(main.app) as client:
            yield client, mock_llm_service_class.return_value, main


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
        main.travel_search_service = Mock()
        main.travel_search_service.search.return_value = TravelSearchResult(
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
