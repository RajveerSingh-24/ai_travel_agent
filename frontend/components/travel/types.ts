export type Message = {
  role: "user" | "assistant";
  content: string;
};

export type Recommendation = {
  flight: {
    id: string;
    airline: string;
    origin: string;
    destination: string;
    departure_date: string;
    return_date: string;
    price: number;
    currency: string;
    direct: boolean;
    duration_minutes: number;
  };
  hotel: {
    id: string;
    name: string;
    destination: string;
    rating: number;
    price_per_night: number;
    total_price: number;
    currency: string;
  };
  total_price: number;
  score: number;
};

export type TravelApproval = {
  approval_id: string;
  session_id: string;
  selected_recommendation_ids: string[];
  status: "pending" | "approved" | "rejected";
};

export type BookingResult = {
  booking_id: string;
  status: "pending" | "confirmed" | "failed";
  selected_flight_id: string;
  selected_hotel_id: string;
  total_price: number;
  currency: string;
};

export type TravelPlanResponse = {
  session_id: string;
  constraints: {
    origin: string | null;
    destination: string | null;
    departure_date: string | null;
    return_date: string | null;
    duration_days: number | null;
    travellers: number | null;
    budget: number | null;
    currency: string | null;
    direct_flight: boolean | null;
    hotel_rating: number | null;
  };
  is_complete: boolean;
  missing_fields: string[];
  clarification_message: string | null;
  recommendations: Recommendation[] | null;
  pending_approval: TravelApproval | null;
};