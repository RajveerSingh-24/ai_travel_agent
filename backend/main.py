import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

from schemas.travel import TravelConstraints
from services.llm_service import LLMService

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
