from typing import Optional

from pydantic import BaseModel, Field

from schemas.travel import TravelConstraints


class TravelPlanRequest(BaseModel):
    """Request model for a session-aware travel planning message."""

    session_id: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Identifier for the travel-planning session",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language travel planning message",
    )


class TravelPlanResponse(BaseModel):
    """Response model for a session-aware travel planning message."""

    session_id: str
    constraints: TravelConstraints
    is_complete: bool
    missing_fields: list[str]
    clarification_message: Optional[str]
