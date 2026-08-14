from schemas.travel import TravelConstraints


def merge_travel_constraints(
    existing: TravelConstraints, new: TravelConstraints
) -> TravelConstraints:
    """
    Merge newly extracted travel constraints into previously collected constraints.

    Preserves existing values when new constraints contain None.
    Uses new values when explicitly provided.
    Returns a new TravelConstraints object without mutating inputs.

    Args:
        existing: Previously collected travel constraints
        new: Newly extracted travel constraints from user input

    Returns:
        TravelConstraints: Merged constraints with new values applied where provided
    """
    return TravelConstraints(
        origin=new.origin if new.origin is not None else existing.origin,
        destination=(
            new.destination if new.destination is not None else existing.destination
        ),
        departure_date=(
            new.departure_date
            if new.departure_date is not None
            else existing.departure_date
        ),
        return_date=(
            new.return_date if new.return_date is not None else existing.return_date
        ),
        duration_days=(
            new.duration_days
            if new.duration_days is not None
            else existing.duration_days
        ),
        travellers=(
            new.travellers if new.travellers is not None else existing.travellers
        ),
        budget=new.budget if new.budget is not None else existing.budget,
        currency=new.currency if new.currency is not None else existing.currency,
        direct_flight=(
            new.direct_flight
            if new.direct_flight is not None
            else existing.direct_flight
        ),
        hotel_rating=(
            new.hotel_rating if new.hotel_rating is not None else existing.hotel_rating
        ),
    )
