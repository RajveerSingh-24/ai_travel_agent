from services.constraint_validator import ValidationResult


# Mapping of missing fields to clarification questions
FIELD_TO_QUESTION = {
    "origin": "What city will you be departing from?",
    "destination": "Where would you like to travel?",
    "departure_date": "What date would you like to depart?",
    "travellers": "How many people will be travelling?",
    "return_date or duration_days": "How many days would you like to stay?",
}


def generate_clarification_message(result: ValidationResult) -> str:
    """
    Generate a natural-language clarification message based on missing fields.

    If all required travel information is provided, returns a confirmation message.
    If fields are missing, returns a single readable message combining all needed questions.

    Args:
        result: ValidationResult from validate_travel_constraints()

    Returns:
        str: Natural-language clarification or confirmation message
    """
    if result.is_complete:
        return "Great! I have all the information needed to help you plan your trip."

    # Map missing fields to questions
    questions = []
    for missing_field in result.missing_fields:
        if missing_field in FIELD_TO_QUESTION:
            questions.append(FIELD_TO_QUESTION[missing_field])

    if not questions:
        # Fallback if a missing field is not in the mapping
        return "Please provide additional travel information to continue."

    # Combine questions into a single message
    if len(questions) == 1:
        return questions[0]

    # For multiple questions, join with newlines and prefixes
    message_parts = ["To help you plan your trip, I need to know:"]
    for i, question in enumerate(questions, 1):
        message_parts.append(f"{i}. {question}")

    return "\n".join(message_parts)
