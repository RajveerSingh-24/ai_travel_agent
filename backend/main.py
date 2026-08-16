import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

from schemas.travel import TravelConstraints
from schemas.api import (
    TravelApprovalRequest,
    TravelApprovalResponse,
    TravelBookingRequest,
    TravelBookingResponse,
    TravelPlanRequest,
    TravelPlanResponse,
)
from services.llm_service import LLMService
from services.approval_service import TravelApprovalService
from services.booking_service import BookingService
from services.providers.duffel_flight_provider import DuffelFlightProvider
from services.providers.duffel_hotel_provider import DuffelHotelProvider
from services.providers.mock_booking_provider import MockBookingProvider
from services.providers.mock_flight_provider import MockFlightProvider
from services.providers.mock_hotel_provider import MockHotelProvider
from services.recommendation_service import (
    TravelRecommendation,
    TravelRecommendationService,
)
from services.search_service import TravelSearchService
from services.travel_orchestrator import TravelOrchestrator
from services.langgraph_orchestrator import LangGraphTravelOrchestrator

app = FastAPI(title="AI Travel Agent Backend")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TravelParseRequest(BaseModel):
    """Request model for travel parsing endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language travel request from user",
    )


class TravelParseResponse(BaseModel):
    """Response model for travel parsing endpoint."""

    constraints: TravelConstraints
    message: str = Field(default="Successfully parsed travel request")


# Initialize LLM service
try:
    llm_service = LLMService()
except ValueError as e:
    llm_service = None
    llm_error = str(e)


# Initialize the session-aware travel planning service.
try:
    travel_orchestrator = TravelOrchestrator()
except ValueError as e:
    travel_orchestrator = None
    travel_orchestrator_error = str(e)

def create_travel_search_service() -> TravelSearchService:
    """Create the travel search service from environment configuration."""
    use_duffel = os.getenv("USE_DUFFEL", "").lower() == "true"
    use_duffel_hotels = os.getenv("USE_DUFFEL_HOTELS", "").lower() == "true"

    flight_provider = (
        DuffelFlightProvider()
        if use_duffel
        else MockFlightProvider()
    )

    hotel_provider = (
        DuffelHotelProvider()
        if use_duffel_hotels
        else MockHotelProvider()
    )

    return TravelSearchService(
        flight_provider,
        hotel_provider,
    )

# Use the mock provider by default.
# Set USE_DUFFEL=true to explicitly enable the real Duffel provider.
travel_search_service = create_travel_search_service()

travel_recommendation_service = TravelRecommendationService()
travel_approval_service = TravelApprovalService()
booking_service = BookingService(MockBookingProvider())


# Initialize the LangGraph travel orchestrator service.
try:
    langgraph_orchestrator = LangGraphTravelOrchestrator(
        llm_service=llm_service,
        search_service=travel_search_service,
        recommendation_service=travel_recommendation_service,
    )
except ValueError as e:
    langgraph_orchestrator = None
    langgraph_orchestrator_error = str(e)


# Process-local state for the prototype's travel-planning sessions.
session_constraints: dict[str, TravelConstraints] = {}
session_recommendations: dict[str, list[TravelRecommendation]] = {}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/api/travel/parse", response_model=TravelParseResponse)
async def parse_travel_request(request: TravelParseRequest):
    """
    Parse a natural language travel request and extract structured constraints.

    Args:
        request: Travel parse request containing user message

    Returns:
        TravelParseResponse: Structured travel constraints

    Raises:
        HTTPException: If API key is missing, request is invalid, or parsing fails
    """
    if not llm_service:
        raise HTTPException(
            status_code=503,
            detail="LLM service unavailable: " + llm_error,
        )

    try:
        constraints = llm_service.parse_travel_request(request.message)
        return TravelParseResponse(constraints=constraints)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while parsing travel request: {str(e)}",
        )


@app.post("/api/travel/plan", response_model=TravelPlanResponse)
async def plan_travel(request: TravelPlanRequest):
    """Process a travel-planning message while retaining session constraints."""
    if not langgraph_orchestrator:
        raise HTTPException(
            status_code=503,
            detail="LangGraph travel orchestrator unavailable: " + langgraph_orchestrator_error,
        )

    try:
        # Run the LangGraph workflow
        state = langgraph_orchestrator.process_message(
            request.session_id,
            request.message,
        )

        constraints = state.get("constraints")
        validation = state.get("validation")
        clarification_message = state.get("clarification_message")
        recommendations = state.get("recommendations")

        is_complete = validation.is_complete if validation else False
        missing_fields = validation.missing_fields if validation else []

        pending_approval = None
        if is_complete:
            if request.selected_recommendation_ids:
                selected_ids = set(request.selected_recommendation_ids)
                is_selected_recommendation = any(
                    selected_ids
                    == {recommendation.flight.id, recommendation.hotel.id}
                    for recommendation in (recommendations or [])
                )
                if not is_selected_recommendation:
                    raise ValueError(f"Selected recommendation is not available. selected_ids: {selected_ids}, recs: {[{r.flight.id, r.hotel.id} for r in (recommendations or [])]}")
                pending_approval = travel_approval_service.create_pending_approval(
                    request.session_id,
                    request.selected_recommendation_ids,
                )
        elif request.selected_recommendation_ids:
            raise ValueError("A recommendation can only be selected for a complete plan")

        if recommendations is not None:
            session_recommendations[request.session_id] = recommendations

        return TravelPlanResponse(
            session_id=request.session_id,
            constraints=constraints,
            is_complete=is_complete,
            missing_fields=missing_fields,
            clarification_message=clarification_message,
            recommendations=recommendations,
            pending_approval=pending_approval,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while planning travel: {str(e)}",
        )


def approval_http_error(error: ValueError) -> HTTPException:
    """Map approval service errors to HTTP responses."""
    error_message = str(error)
    status_code = {
        "Unknown approval ID": 404,
        "Approval does not belong to this session": 403,
        "Approval has already been resolved": 409,
        "Approval is still pending": 409,
        "Approval was rejected": 409,
    }.get(error_message, 400)
    return HTTPException(status_code=status_code, detail=error_message)


@app.post("/api/travel/approval", response_model=TravelApprovalResponse)
async def resolve_travel_approval(request: TravelApprovalRequest):
    """Approve or reject a pending travel recommendation approval."""
    try:
        if request.action == "approve":
            approval = travel_approval_service.approve(
                request.session_id,
                request.approval_id,
            )
        else:
            approval = travel_approval_service.reject(
                request.session_id,
                request.approval_id,
            )
        return TravelApprovalResponse(approval=approval)
    except ValueError as e:
        raise approval_http_error(e)


@app.post("/api/travel/book", response_model=TravelBookingResponse)
async def book_travel(request: TravelBookingRequest):
    """Book the approved flight and hotel selection for a travel session."""
    try:
        approval = travel_approval_service.get_approved(
            request.session_id,
            request.approval_id,
        )
        recommendations = session_recommendations.get(request.session_id, [])
        selected_ids = set(approval.selected_recommendation_ids)
        recommendation = next(
            (
                recommendation
                for recommendation in recommendations
                if selected_ids
                == {recommendation.flight.id, recommendation.hotel.id}
            ),
            None,
        )
        constraints = langgraph_orchestrator.get_constraints(request.session_id)
        if recommendation is None or constraints is None:
            raise HTTPException(
                status_code=404,
                detail="Approved recommendation is not available for this session",
            )

        booking = booking_service.book(
            request.approval_id,
            recommendation.flight,
            recommendation.hotel,
            constraints,
        )
        return TravelBookingResponse(booking=booking)
    except ValueError as e:
        raise approval_http_error(e)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while booking travel: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
