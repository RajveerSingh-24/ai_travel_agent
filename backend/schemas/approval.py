from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ApprovalStatus(str, Enum):
    """Possible states for a travel recommendation approval."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class TravelApproval(BaseModel):
    """Provider-independent state for a selected travel recommendation."""

    approval_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    selected_recommendation_ids: list[Annotated[str, Field(min_length=1)]] = Field(
        ..., min_length=1
    )
    status: ApprovalStatus = ApprovalStatus.PENDING

    model_config = ConfigDict(frozen=True)
