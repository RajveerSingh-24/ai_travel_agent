from dataclasses import dataclass
from typing import Optional

from schemas.travel import TravelConstraints
from services.clarification_service import generate_clarification_message
from services.constraint_merger import merge_travel_constraints
from services.constraint_validator import ValidationResult, validate_travel_constraints
from services.llm_service import LLMService


@dataclass
class TravelOrchestratorResult:
    """Result of processing a travel-planning message."""

    constraints: TravelConstraints
    validation: ValidationResult
    clarification_message: Optional[str]


class TravelOrchestrator:
    """Coordinates travel constraint extraction, merging, and validation."""

    def __init__(self):
        self.llm_service = LLMService()

    def process_message(
        self,
        user_message: str,
        existing_constraints: Optional[TravelConstraints] = None,
    ) -> TravelOrchestratorResult:
        """Process a message and return its collected travel-planning state."""
        extracted_constraints = self.llm_service.parse_travel_request(user_message)

        constraints = (
            merge_travel_constraints(existing_constraints, extracted_constraints)
            if existing_constraints is not None
            else extracted_constraints
        )
        validation = validate_travel_constraints(constraints)
        clarification_message = (
            generate_clarification_message(validation)
            if not validation.is_complete
            else None
        )

        return TravelOrchestratorResult(
            constraints=constraints,
            validation=validation,
            clarification_message=clarification_message,
        )
