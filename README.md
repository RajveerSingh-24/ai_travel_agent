# AI Travel Agent

## Project Title and Concise Description
**AI Travel Agent** is an intelligent travel planning assistant. It uses natural language processing to understand user travel requirements, orchestrates a conversational flow to gather missing information, searches for flights and hotels, and facilitates a human-in-the-loop approval process before final booking.

## Project Objective / Problem Statement
Planning a trip often involves juggling multiple constraints (dates, budget, locations) across different platforms. The objective of this project is to provide a unified, conversational interface where an AI agent handles the complex orchestration of extracting constraints, finding valid travel options, and managing the booking flow, reducing friction for the user.

## Screenshots (Demo)
### Main Screen

<img width="1710" height="979" alt="Screenshot 2026-08-20 at 11 26 36 PM" src="https://github.com/user-attachments/assets/666a8415-1af8-413b-9d44-f0786deb27ce" />

### Chat and Recommendation

<img width="1710" height="984" alt="Screenshot 2026-08-17 at 1 35 43 PM" src="https://github.com/user-attachments/assets/b93f64d1-4b63-4318-8160-8bfac75bc20e" />

### Selection and Booking Approval

<img width="1710" height="984" alt="Screenshot 2026-08-17 at 1 36 03 PM" src="https://github.com/user-attachments/assets/26e0ebc8-e5f5-471d-8270-bf6e3f9dd91c" />

### Booking Confirmation

<img width="1710" height="984" alt="Screenshot 2026-08-17 at 1 36 18 PM" src="https://github.com/user-attachments/assets/7c2713fc-b3c5-464a-927a-b2d9fad2838f" />

### Confirmation Successful (Receipt and Summary)

<img width="1710" height="979" alt="Screenshot 2026-08-20 at 11 30 01 PM" src="https://github.com/user-attachments/assets/7f5220ab-8699-4bf2-bb2e-868779593289" />

## Key Features
- **Natural Language Parsing:** Extracts travel constraints (origin, destination, dates, budget, etc.) from conversational text.
- **Conversational Orchestration:** Uses an AI workflow to ask clarifying questions if essential constraints are missing.
- **Dynamic Search:** Integrates with travel APIs to find flights and hotels based on the extracted constraints.
- **Human-in-the-Loop:** Requires explicit user approval for recommended itineraries before proceeding to booking.
- **Mock and Real Providers:** Supports seamless switching between mock data (for testing) and real travel APIs (like Duffel).

## High-Level Architecture
```
                                  ┌─────────────────────┐
                                  │   User / Browser    │
                                  └──────────┬──────────┘
                                             │
                                             ▼
                                  ┌─────────────────────┐
                                  │ Next.js Frontend    │
                                  │ Chat + Recommendations
                                  │ Approval + Booking  │
                                  └──────────┬──────────┘
                                             │ REST API
                                             ▼
                                  ┌─────────────────────┐
                                  │   FastAPI Backend   │
                                  └──────────┬──────────┘
                                             │
                                             ▼
                               ┌──────────────────────────┐
                               │ LangGraph Orchestrator   │
                               └────────────┬─────────────┘
                                            │
                            ┌───────────────┼────────────────┐
                            ▼               ▼                ▼
                      ┌──────────┐   ┌────────────┐   ┌─────────────┐
                      │ Gemini   │   │ Validation │   │ Search      │
                      │ LLM      │   │ / State    │   │ Services    │
                      └──────────┘   └────────────┘   └──────┬──────┘
                                                             │
                                                ┌────────────┴────────────┐
                                                ▼                         ▼
                                         Flight Provider           Hotel Provider
                                         Mock / Duffel             Mock / Duffel
                                                │                         │
                                                └────────────┬────────────┘
                                                             ▼
                                                    Recommendations
                                                             │
                                                             ▼
                                                    Human Approval
                                                             │
                                                             ▼
                                                      Booking Service
                                                       Mock Provider
```

### How the AI Agent Workflow Works
```
                                            User Message
                                                 │
                                                 ▼
                                            LLM extracts TravelConstraints
                                                 │
                                                 ▼
                                            Validate constraints
                                                 │
                                                 ├── Missing information ──► Ask clarification
                                                 │                              │
                                                 │                              └──► User responds
                                                 │
                                                 ▼
                                            All required information present
                                                 │
                                                 ▼
                                            Search flights + hotels
                                                 │
                                                 ▼
                                            Generate recommendations
                                                 │
                                                 ▼
                                            User selects option
                                                 │
                                                 ▼
                                            Create pending approval
                                                 │
                                                 ├── Reject ──► Return to options
                                                 │
                                                 ▼
                                            User approves
                                                 │
                                                 ▼
                                            Booking service
                                                 │
                                                 ▼
                                            Booking confirmation
 ```           
1. **Extraction:** The user provides a natural language prompt. The LLM extracts structured `TravelConstraints`.
2. **Validation:** The system checks if all required fields are present. If not, the LLM generates a clarifying question.
3. **Search & Recommendation:** Once constraints are complete, the system queries travel providers for flight and hotel options, then recommends the best matches.
4. **Approval & Booking:** The user selects and approves a recommendation. The backend transitions this to a pending approval state, which can then be booked.

### Frontend Technology and UI Flow
- **Tech Stack:** Next.js (App Router), React, Tailwind CSS, TypeScript.
- **UI Flow:** The user interacts with a chat-like interface. When recommendations are ready, they are displayed in a `RecommendationPanel`. The user can select a plan, approve it, and simulate booking.

### Backend Technology and API Structure
- **Tech Stack:** Python, FastAPI, Pydantic, pytest.
- **API Structure:** RESTful JSON endpoints handling parsing, planning, approval, and booking.

### LangGraph Orchestration and the Role of the LLM
- **LangGraph:** Used to model the conversational state machine (`LangGraphTravelOrchestrator`). It tracks the state of the conversation (extracted constraints, missing fields, generated recommendations).
- **LLM (Gemini):** Used via `LLMService` to parse natural language into structured Pydantic models and to generate human-readable clarification messages.

### Flight and Hotel Provider Integration
- **Duffel vs Mock:** The `TravelSearchService` abstracts the underlying data source. Depending on environment variables (`USE_DUFFEL`, `USE_DUFFEL_HOTELS`), it instantiates either `DuffelFlightProvider`/`DuffelHotelProvider` or `MockFlightProvider`/`MockHotelProvider`.
- **Current Status:** Flight search has Duffel integration. Hotel search has Duffel support configured via environment variables. Booking is currently hardcoded to use `MockBookingProvider()`.

### Human-in-the-Loop Approval Flow
The system does not book automatically. A user must select specific flight and hotel recommendations. This generates a pending approval (`travel_approval_service.create_pending_approval`). The user must explicitly approve this plan via the `/api/travel/approval` endpoint before it can be finalized.

### Booking Flow
After approval, the frontend calls `/api/travel/book` with the `approval_id` and `session_id`. The backend verifies the approval and delegates the action to the `BookingService` (currently mocked).

### Current Limitations / Prototype Status
- **Persistence:** Session state and approvals are stored in process-local memory (`dict`), meaning data is lost on server restart.
- **Booking Integration:** Real booking via Duffel is not fully implemented; it uses a mock provider.
- **Tests:** There are a few failing tests related to Duffel mapping and booking API edge cases.

## Project Structure

A detailed look at the important files and directories in this repository:

```
.
├── backend/
│   ├── main.py                          # FastAPI app, API routes, dependency injection
│   ├── schemas/
│   │   ├── api.py                       # Request/Response models for endpoints
│   │   ├── travel.py                    # TravelConstraints and related domain models
│   │   └── ...                          # Other Pydantic schemas (approval, booking, search)
│   ├── services/
│   │   ├── langgraph_orchestrator.py    # The LangGraph state machine definition
│   │   ├── llm_service.py               # Gemini API integration for parsing & clarifying
│   │   ├── search_service.py            # Interfaces with travel providers
│   │   ├── recommendation_service.py    # Pairs flights/hotels based on constraints
│   │   ├── approval_service.py          # Handles the human-in-the-loop pending states
│   │   ├── booking_service.py           # Validates approvals and simulates booking
│   │   └── providers/                   # External API implementations
│   │       ├── duffel_flight_provider.py
│   │       ├── duffel_hotel_provider.py
│   │       ├── mock_flight_provider.py
│   │       └── ...
│   ├── tests/                           # Comprehensive pytest suite (140+ tests)
│   ├── requirements.txt                 # Python dependencies
│   └── .env                             # Environment variables (API keys, toggles)
│
└── frontend/
    ├── app/
    │   ├── page.tsx                     # Main chat interface and layout
    │   └── globals.css                  # Tailwind styles
    ├── components/
    │   ├── chat/                        # User and AI message bubble components
    │   ├── travel/                      # Travel specific UI components
    │   │   └── RecommendationPanel.tsx  # Displays flight/hotel pairings for approval
    │   ├── booking/                     # Booking confirmation views
    │   └── ui/                          # Reusable UI elements (buttons, inputs)
    ├── package.json                     # Node.js dependencies
    └── tailwind.config.js               # Tailwind configuration
```

## Prerequisites
- Node.js (v18+)
- Python (3.10+)
- A Gemini API Key
- A Duffel API Token (optional, for real flight data)

## Environment Variables Required
Create a `.env` file in the `backend/` directory:
```
GEMINI_API_KEY=your_gemini_api_key
DUFFEL_API_TOKEN=your_duffel_api_token
USE_DUFFEL=true|false
USE_DUFFEL_HOTELS=true|false
```

## Exact Local Setup Instructions

### How to run the backend
```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### How to run the frontend
```
cd frontend
npm install
npm run dev
```

## API Endpoint Summary
- `GET /health` - Health check.
- `POST /api/travel/parse` - Parses a user message into travel constraints.
- `POST /api/travel/plan` - Core endpoint that runs the LangGraph workflow, returning constraints, clarifications, or recommendations.
- `POST /api/travel/approval` - Approves or rejects a selected travel recommendation.
- `POST /api/travel/book` - Books an approved travel recommendation.

## Testing Instructions and Current Test Status
To run the backend tests:
```
cd backend
source venv/bin/activate
pytest tests/
```
**Current Status:** 140 tests collected. 137 tests pass, 3 tests fail (mostly related to provider mapping and booking endpoint repeat logic).

## Future Improvements
- **Persistent Storage:** Replace in-memory dictionaries with a database (e.g., PostgreSQL, Redis) for session and LangGraph state management.
- **Full Real Booking:** Implement Duffel booking APIs instead of the mock provider.
- **Test Fixes:** Resolve the 3 failing tests to ensure 100% pass rate.
- **User Authentication:** Add user accounts to track trips and preferences across sessions.

## Deployment Considerations
- **Frontend:** Next.js application deployable on platforms such as Vercel.
- **Backend:** Can be deployed as a Docker container on platforms like Render, Railway, AWS ECS, or Google Cloud Run.
- **State Management:** When scaling the backend beyond a single instance, the process-local memory must be replaced with a distributed cache (e.g., Redis) to manage user sessions and approvals.
