import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

from schemas.travel import TravelConstraints
from schemas.api import TravelPlanRequest, TravelPlanResponse
from services.llm_service import LLMService
from services.providers.mock_flight_provider import MockFlightProvider
from services.providers.mock_hotel_provider import MockHotelProvider
from services.recommendation_service import TravelRecommendationService
from services.search_service import TravelSearchService
from services.travel_orchestrator import TravelOrchestrator

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


# Process-local state for the prototype's travel-planning sessions.
session_constraints: dict[str, TravelConstraints] = {}

# Offline search and recommendation services for the prototype.
travel_search_service = TravelSearchService(
    MockFlightProvider(),
    MockHotelProvider(),
)
travel_recommendation_service = TravelRecommendationService()


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
    if not travel_orchestrator:
        raise HTTPException(
            status_code=503,
            detail="Travel orchestrator unavailable: " + travel_orchestrator_error,
        )

    try:
        existing_constraints = session_constraints.get(request.session_id)
        result = travel_orchestrator.process_message(
            request.message,
            existing_constraints,
        )
        session_constraints[request.session_id] = result.constraints

        recommendations = None
        if result.validation.is_complete:
            search_results = travel_search_service.search(result.constraints)
            recommendations = travel_recommendation_service.recommend(
                result.constraints,
                search_results.flights,
                search_results.hotels,
            )

        return TravelPlanResponse(
            session_id=request.session_id,
            constraints=result.constraints,
            is_complete=result.validation.is_complete,
            missing_fields=result.validation.missing_fields,
            clarification_message=result.clarification_message,
            recommendations=recommendations,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while planning travel: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
