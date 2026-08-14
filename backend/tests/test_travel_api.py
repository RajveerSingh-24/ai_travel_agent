import importlib
from unittest.mock import patch

import httpx
import pytest
from fastapi.testclient import TestClient

from schemas.travel import TravelConstraints


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
            yield client, mock_llm_service_class.return_value


class TestTravelPlanEndpoint:
    """Tests for the session-aware travel planning endpoint."""

    def test_returns_complete_structured_plan(self, client_and_llm_service):
        client, mock_llm_service = client_and_llm_service
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
        assert response.json() == {
            "session_id": "session-1",
            "constraints": {
                "origin": "New York",
                "destination": "Paris",
                "departure_date": "2026-09-01",
                "return_date": "2026-09-15",
                "duration_days": None,
                "travellers": 2,
                "budget": None,
                "currency": None,
                "direct_flight": None,
                "hotel_rating": None,
            },
            "is_complete": True,
            "missing_fields": [],
            "clarification_message": None,
        }
        mock_llm_service.parse_travel_request.assert_called_once_with("Plan a Paris trip")

    def test_retains_and_merges_constraints_for_a_session(self, client_and_llm_service):
        client, mock_llm_service = client_and_llm_service
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
        assert second_response.status_code == 200
        assert second_response.json()["constraints"]["origin"] == "New York"
        assert second_response.json()["constraints"]["destination"] == "Paris"
        assert second_response.json()["constraints"]["travellers"] == 2
        assert second_response.json()["is_complete"] is True
        assert second_response.json()["clarification_message"] is None

    def test_rejects_empty_message(self, client_and_llm_service):
        client, mock_llm_service = client_and_llm_service

        response = client.post(
            "/api/travel/plan",
            json={"session_id": "session-3", "message": ""},
        )

        assert response.status_code == 422
        mock_llm_service.parse_travel_request.assert_not_called()

    def test_returns_bad_request_for_invalid_llm_input(self, client_and_llm_service):
        client, mock_llm_service = client_and_llm_service
        mock_llm_service.parse_travel_request.side_effect = ValueError(
            "User message cannot be empty"
        )

        response = client.post(
            "/api/travel/plan",
            json={"session_id": "session-4", "message": "Invalid request"},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "User message cannot be empty"
