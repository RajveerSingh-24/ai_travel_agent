from schemas.travel import TravelConstraints


from pydantic import BaseModel


class ValidationResult(BaseModel):
    """Result of constraint validation."""

    is_complete: bool
    missing_fields: list[str]

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "is_complete": self.is_complete,
            "missing_fields": self.missing_fields,
        }


def validate_travel_constraints(
    constraints: TravelConstraints,
) -> ValidationResult:
    """
    Validate travel constraints for completeness.

    Required fields for flight/hotel search:
    - origin
    - destination
    - departure_date
    - travellers

    For a round trip, require either return_date or duration_days.

    Optional fields:
    - budget
    - currency
    - direct_flight
    - hotel_rating

    Args:
        constraints: TravelConstraints object to validate

    Returns:
        ValidationResult: Contains is_complete flag and list of missing fields
    """
    missing_fields = []

    # Check required fields
    if not constraints.origin:
        missing_fields.append("origin")
    if not constraints.destination:
        missing_fields.append("destination")
    if not constraints.departure_date:
        missing_fields.append("departure_date")
    if constraints.travellers is None:
        missing_fields.append("travellers")

    # For round trip, need either return_date or duration_days
    if not constraints.return_date and constraints.duration_days is None:
        missing_fields.append("return_date or duration_days")

    is_complete = len(missing_fields) == 0

    return ValidationResult(is_complete=is_complete, missing_fields=missing_fields)
