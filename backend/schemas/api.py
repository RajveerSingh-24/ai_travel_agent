from typing import Literal, Optional

from pydantic import BaseModel, Field

from schemas.approval import TravelApproval
from schemas.travel import TravelConstraints
from services.recommendation_service import TravelRecommendation


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
    selected_recommendation_ids: Optional[list[str]] = Field(
        None,
        min_length=1,
        description="Flight and hotel IDs for the selected recommendation",
    )


class TravelPlanResponse(BaseModel):
    """Response model for a session-aware travel planning message."""

    session_id: str
    constraints: TravelConstraints
    is_complete: bool
    missing_fields: list[str]
    clarification_message: Optional[str]
    recommendations: Optional[list[TravelRecommendation]] = None
    pending_approval: Optional[TravelApproval] = None


class TravelApprovalRequest(BaseModel):
    """Request model for resolving a travel recommendation approval."""

    session_id: str = Field(..., min_length=1)
    approval_id: str = Field(..., min_length=1)
    action: Literal["approve", "reject"]


class TravelApprovalResponse(BaseModel):
    """Response model containing the resolved travel approval state."""

    approval: TravelApproval
