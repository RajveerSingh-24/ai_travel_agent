import json
import os
from typing import Optional
from datetime import datetime
import google.genai as genai
from pydantic import ValidationError

from schemas.travel import TravelConstraints


class LLMService:
    """Service for interacting with Google Gemini API."""

    def __init__(self):
        """Initialize Gemini client with API key from environment."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Please set it in your .env file."
            )
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-3.1-flash-lite"

    def parse_travel_request(self, user_message: str) -> TravelConstraints:
        """
        Parse a natural language travel request and extract structured constraints.

        Args:
            user_message: Natural language travel request from user

        Returns:
            TravelConstraints: Structured travel information

        Raises:
            ValueError: If API key is missing or response is invalid
            ValidationError: If extracted data doesn't match schema
        """
        if not user_message or not user_message.strip():
            raise ValueError("User message cannot be empty")

        # Build the prompt with schema instructions
        schema_json = TravelConstraints.model_json_schema()
        prompt = f"""You are a travel planning assistant. Extract travel constraints from the user's message.
        
Return a JSON object matching this exact schema:
{json.dumps(schema_json, indent=2)}

Important notes:
- Use YYYY-MM-DD format for dates
- If a travel constraint is not explicitly provided by the user, return null. Never invent or infer missing travel constraints. Do not calculate or infer return_date unless the user explicitly provides it.
- If the user does not explicitly specify a currency, return null; never infer or default the currency from location, language, or system locale
- Ensure the JSON is valid and complete

User message: {user_message}

Respond with ONLY the JSON object, no markdown formatting or code blocks."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )

            if not response.text:
                raise ValueError("Empty response from Gemini API")

            # Parse the response text as JSON
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            constraints_dict = json.loads(response_text)

            # Validate and return as TravelConstraints
            return TravelConstraints(**constraints_dict)

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse Gemini response as JSON: {str(e)}")
        except ValidationError as e:
            raise ValueError(
                f"Gemini response doesn't match travel constraints schema: {str(e)}"
            )
        except Exception as e:
            raise ValueError(f"Gemini API error: {str(e)}")
