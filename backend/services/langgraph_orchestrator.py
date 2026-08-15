from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END, START

from schemas.travel import TravelConstraints
from services.llm_service import LLMService
from services.constraint_merger import merge_travel_constraints
from services.constraint_validator import ValidationResult, validate_travel_constraints
from services.clarification_service import generate_clarification_message
from services.search_service import TravelSearchService
from services.recommendation_service import TravelRecommendation, TravelRecommendationService
from services.providers.mock_flight_provider import MockFlightProvider
from services.providers.mock_hotel_provider import MockHotelProvider


class TravelAgentState(TypedDict):
    """Represent the state passed between nodes in the travel agent workflow."""

    session_id: str
    user_message: str
    constraints: Optional[TravelConstraints]
    validation: Optional[ValidationResult]
    clarification_message: Optional[str]
    recommendations: Optional[List[TravelRecommendation]]


class LangGraphTravelOrchestrator:
    """Orchestrates travel planning flow using a LangGraph state machine."""

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        search_service: Optional[TravelSearchService] = None,
        recommendation_service: Optional[TravelRecommendationService] = None,
    ):
        self.llm_service = llm_service or LLMService()
        self.search_service = search_service or TravelSearchService(
            MockFlightProvider(),
            MockHotelProvider(),
        )
        self.recommendation_service = recommendation_service or TravelRecommendationService()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(TravelAgentState)

        def parse_and_merge_node(state: TravelAgentState) -> dict:
            # 1. Parse constraints using LLMService
            extracted = self.llm_service.parse_travel_request(state["user_message"])
            
            # 2. Merge with existing constraints if they exist
            existing = state.get("constraints")
            if existing is not None:
                merged = merge_travel_constraints(existing, extracted)
            else:
                merged = extracted
            return {"constraints": merged}

        def validate_node(state: TravelAgentState) -> dict:
            validation = validate_travel_constraints(state["constraints"])
            return {"validation": validation}

        def clarify_node(state: TravelAgentState) -> dict:
            msg = generate_clarification_message(state["validation"])
            return {"clarification_message": msg}

        def search_and_recommend_node(state: TravelAgentState) -> dict:
            constraints = state["constraints"]
            search_results = self.search_service.search(constraints)
            recommendations = self.recommendation_service.recommend(
                constraints,
                search_results.flights,
                search_results.hotels,
            )
            return {"recommendations": recommendations}

        # Add nodes
        workflow.add_node("parse_and_merge", parse_and_merge_node)
        workflow.add_node("validate", validate_node)
        workflow.add_node("clarify", clarify_node)
        workflow.add_node("search_and_recommend", search_and_recommend_node)

        # Set execution flow edges
        workflow.add_edge(START, "parse_and_merge")
        workflow.add_edge("parse_and_merge", "validate")

        # Routing decision logic based on validation results
        def route_next(state: TravelAgentState):
            if state.get("validation") and state["validation"].is_complete:
                return "search_and_recommend"
            return "clarify"

        workflow.add_conditional_edges(
            "validate",
            route_next,
            {
                "search_and_recommend": "search_and_recommend",
                "clarify": "clarify",
            }
        )

        workflow.add_edge("clarify", END)
        workflow.add_edge("search_and_recommend", END)

        return workflow.compile()

    def process_message(
        self,
        session_id: str,
        user_message: str,
        existing_constraints: Optional[TravelConstraints] = None,
    ) -> TravelAgentState:
        """Run the LangGraph travel agent workflow for the given user message."""
        initial_state = TravelAgentState(
            session_id=session_id,
            user_message=user_message,
            constraints=existing_constraints,
            validation=None,
            clarification_message=None,
            recommendations=None,
        )
        return self.graph.invoke(initial_state)
