"use client";

import { useState } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

type Recommendation = {
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

type TravelApproval = {
  approval_id: string;
  session_id: string;
  selected_recommendation_ids: string[];
  status: "pending" | "approved" | "rejected";
};

type BookingResult = {
  booking_id: string;
  status: "pending" | "confirmed" | "failed";
  selected_flight_id: string;
  selected_hotel_id: string;
  total_price: number;
  currency: string;
};
type TravelPlanResponse = {
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

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm your AI Travel Agent. Tell me where you'd like to travel, and I'll help you plan your trip.",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const [selectedRecommendation, setSelectedRecommendation] =
    useState<Recommendation | null>(null);

  const [pendingApproval, setPendingApproval] =
    useState<TravelApproval | null>(null);
 
  const [booking, setBooking] = useState<BookingResult | null>(null);

  const selectRecommendation = async (
    recommendation: Recommendation
  ) => {
    setLoading(true);
    setSelectedRecommendation(recommendation);

    try {
      const response = await fetch(
        "http://localhost:8000/api/travel/plan",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            session_id: sessionId,
            message: "I would like to select this recommendation.",
            selected_recommendation_ids: [
              recommendation.flight.id,
              recommendation.hotel.id,
            ],
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail ||
            `Request failed with status ${response.status}`
        );
      }

      const data: TravelPlanResponse = await response.json();

      if (data.pending_approval) {
        setPendingApproval(data.pending_approval);
      }
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            error instanceof Error
              ? `Sorry, I couldn't select that option: ${error.message}`
              : "Sorry, I couldn't select that option.",
        },
      ]);

      setSelectedRecommendation(null);
    } finally {
      setLoading(false);
    }
  };

 const approveRecommendation = async () => {
    if (!pendingApproval) {
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        "http://localhost:8000/api/travel/approval",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            session_id: sessionId,
            approval_id: pendingApproval.approval_id,
            action: "approve",
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail ||
            `Request failed with status ${response.status}`
        );
      }

      const data: { approval: TravelApproval } =
        await response.json();

      setPendingApproval(data.approval);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "Your selection has been approved. I can now proceed with the booking.",
        },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            error instanceof Error
              ? `Sorry, I couldn't approve the selection: ${error.message}`
              : "Sorry, I couldn't approve the selection.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const rejectRecommendation = async () => {
    if (!pendingApproval) {
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        "http://localhost:8000/api/travel/approval",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            session_id: sessionId,
            approval_id: pendingApproval.approval_id,
            action: "reject",
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail ||
            `Request failed with status ${response.status}`
        );
      }

      const data: { approval: TravelApproval } =
        await response.json();

      setPendingApproval(data.approval);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "Your selection was rejected. You can choose another travel option.",
        },
      ]);

      setSelectedRecommendation(null);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            error instanceof Error
              ? `Sorry, I couldn't reject the selection: ${error.message}`
              : "Sorry, I couldn't reject the selection.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const bookRecommendation = async () => {
    if (
      !pendingApproval ||
      pendingApproval.status !== "approved"
    ) {
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        "http://localhost:8000/api/travel/book",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            session_id: sessionId,
            approval_id: pendingApproval.approval_id,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail ||
            `Request failed with status ${response.status}`
        );
      }

      const data: { booking: BookingResult } =
        await response.json();

      setBooking(data.booking);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: `Booking confirmed! Your booking ID is ${data.booking.booking_id}.`,
        },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            error instanceof Error
              ? `Sorry, I couldn't complete the booking: ${error.message}`
              : "Sorry, I couldn't complete the booking.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const [recommendations, setRecommendations] = useState<
    Recommendation[] | null
  >(null);

  const [sessionId] = useState(
    () => `frontend-${crypto.randomUUID()}`
  );

  const sendMessage = async () => {
    const message = input.trim();

    if (!message || loading) {
      return;
    }

    setInput("");
    setLoading(true);
    setRecommendations(null);

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: message,
      },
    ]);

    try {
      const response = await fetch("http://localhost:8000/api/travel/plan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          message,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail || `Request failed with status ${response.status}`
        );
      }

      const data: TravelPlanResponse = await response.json();

      if (data.clarification_message) {
        setMessages((previous) => [
          ...previous,
          {
            role: "assistant",
            content: data.clarification_message!,
          },
        ]);
      }

      if (data.recommendations && data.recommendations.length > 0) {
        setRecommendations(data.recommendations);

        setMessages((previous) => [
          ...previous,
          {
            role: "assistant",
            content:
              "Great! I found some travel options for you. Take a look below.",
          },
        ]);
      }

      if (
        data.is_complete &&
        (!data.recommendations || data.recommendations.length === 0)
      ) {
        setMessages((previous) => [
          ...previous,
          {
            role: "assistant",
            content:
              "Your trip details are complete, but I couldn't find any matching options.",
          },
        ]);
      }
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            error instanceof Error
              ? `Sorry, something went wrong: ${error.message}`
              : "Sorry, something went wrong while planning your trip.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      sendMessage();
    }
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;

    return `${hours}h ${remainingMinutes}m`;
  };

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto flex min-h-screen max-w-5xl flex-col px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-3xl font-bold">
            ✈️ AI Travel Agent
          </h1>

          <p className="mt-2 text-slate-400">
            Tell me about your trip and I&apos;ll help you find the best options.
          </p>
        </header>

        {/* Chat */}
        <section className="flex-1 rounded-2xl border border-slate-800 bg-slate-900 p-4 shadow-xl">
          <div className="space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === "user"
                    ? "justify-end"
                    : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    message.role === "user"
                      ? "bg-indigo-600 text-white"
                      : "bg-slate-800 text-slate-100"
                  }`}
                >
                  {message.content.split("\n").map((line, lineIndex) => (
                    <p key={lineIndex} className="leading-6">
                      {line}
                    </p>
                  ))}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="rounded-2xl bg-slate-800 px-4 py-3 text-slate-400">
                  Thinking...
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="mt-6 flex gap-3 border-t border-slate-800 pt-4">
            <input
              type="text"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="e.g. I want to travel from Delhi to Paris..."
              disabled={loading}
              className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-indigo-500"
            />

            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="rounded-xl bg-indigo-600 px-6 py-3 font-semibold transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-slate-700"
            >
              {loading ? "..." : "Send"}
            </button>
          </div>
        </section>

        {/* Recommendations */}
        {recommendations && recommendations.length > 0 && (
          <section className="mt-8">
            <h2 className="mb-4 text-2xl font-bold">
              Recommended Options
            </h2>

            <div className="grid gap-5">
              {recommendations.map((recommendation, index) => (
                <div
                  key={`${recommendation.flight.id}-${recommendation.hotel.id}`}
                  className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg"
                >
                  <div className="mb-5 flex items-center justify-between">
                    <h3 className="text-lg font-semibold">
                      Option {index + 1}
                    </h3>

                    <span className="rounded-full bg-indigo-500/20 px-3 py-1 text-sm text-indigo-300">
                      Score {recommendation.score.toFixed(2)}
                    </span>
                  </div>

                  {/* Flight */}
                  <div className="rounded-xl bg-slate-800 p-4">
                    <p className="mb-2 text-sm font-medium text-indigo-300">
                      ✈️ Flight
                    </p>

                    <div className="flex flex-col justify-between gap-3 md:flex-row">
                      <div>
                        <p className="font-semibold">
                          {recommendation.flight.airline}
                        </p>

                        <p className="text-slate-400">
                          {recommendation.flight.origin} →{" "}
                          {recommendation.flight.destination}
                        </p>
                      </div>

                      <div className="text-left md:text-right">
                        <p className="font-semibold">
                          {recommendation.flight.currency}{" "}
                          {recommendation.flight.price.toFixed(2)}
                        </p>

                        <p className="text-sm text-slate-400">
                          {recommendation.flight.direct
                            ? "Direct"
                            : "Non-direct"}{" "}
                          ·{" "}
                          {formatDuration(
                            recommendation.flight.duration_minutes
                          )}
                        </p>
                      </div>
                    </div>

                    <p className="mt-3 text-sm text-slate-400">
                      {recommendation.flight.departure_date} →{" "}
                      {recommendation.flight.return_date}
                    </p>
                  </div>

                  {/* Hotel */}
                  <div className="mt-4 rounded-xl bg-slate-800 p-4">
                    <p className="mb-2 text-sm font-medium text-indigo-300">
                      🏨 Hotel
                    </p>

                    <div className="flex flex-col justify-between gap-3 md:flex-row">
                      <div>
                        <p className="font-semibold">
                          {recommendation.hotel.name}
                        </p>

                        <p className="text-slate-400">
                          {recommendation.hotel.destination} ·{" "}
                          {recommendation.hotel.rating.toFixed(1)} ⭐
                        </p>
                      </div>

                      <div className="text-left md:text-right">
                        <p className="font-semibold">
                          {recommendation.hotel.currency}{" "}
                          {recommendation.hotel.total_price.toFixed(2)}
                        </p>

                        <p className="text-sm text-slate-400">
                          {recommendation.hotel.currency}{" "}
                          {recommendation.hotel.price_per_night.toFixed(2)}
                          /night
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Total */}
                  <div className="mt-5 flex flex-col gap-4 border-t border-slate-800 pt-5 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <p className="text-sm text-slate-400">
                        Total trip cost
                      </p>

                      <p className="text-xl font-bold">
                        {recommendation.flight.currency}{" "}
                        {recommendation.total_price.toFixed(2)}
                      </p>
                    </div>

                    <button
                      onClick={() => selectRecommendation(recommendation)}
                      disabled={loading}
                      className="rounded-xl bg-indigo-600 px-5 py-3 font-semibold transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-slate-700"
                    >
                      {loading && selectedRecommendation === recommendation
                        ? "Selecting..."
                        : "Select this option"}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
        {pendingApproval && selectedRecommendation && !booking && (
          <section className="mt-8 rounded-2xl border border-amber-500/30 bg-amber-500/10 p-6">
            <h2 className="text-2xl font-bold">
              Review your selection
            </h2>

            <p className="mt-2 text-slate-300">
              You selected{" "}
              <strong>{selectedRecommendation.flight.airline}</strong>{" "}
              +{" "}
              <strong>{selectedRecommendation.hotel.name}</strong>.
            </p>

            <div className="mt-4 rounded-xl bg-slate-900 p-4">
              <p className="text-sm text-slate-400">
                Total trip cost
              </p>

              <p className="mt-1 text-2xl font-bold">
                {selectedRecommendation.flight.currency}{" "}
                {selectedRecommendation.total_price.toFixed(2)}
              </p>
            </div>

            <p className="mt-4 text-sm text-amber-300">
              Approval ID: {pendingApproval.approval_id}
            </p>

            <p className="mt-2 text-sm text-slate-400">
              Status: {pendingApproval.status}
            </p>

            {pendingApproval.status === "pending" && (
              <div className="mt-5 flex flex-col gap-3 sm:flex-row">
                <button
                  onClick={approveRecommendation}
                  disabled={loading}
                  className="flex-1 rounded-xl bg-amber-500 px-5 py-3 font-semibold text-slate-950 transition hover:bg-amber-400 disabled:cursor-not-allowed disabled:bg-slate-600"
                >
                  {loading ? "Processing..." : "Approve & Continue"}
                </button>

                <button
                  onClick={rejectRecommendation}
                  disabled={loading}
                  className="flex-1 rounded-xl border border-red-500/50 bg-red-500/10 px-5 py-3 font-semibold text-red-300 transition hover:bg-red-500/20 disabled:cursor-not-allowed disabled:bg-slate-700"
                >
                  {loading ? "Processing..." : "Reject"}
                </button>
              </div>
            )}

            {pendingApproval.status === "approved" && (
              <button
                onClick={bookRecommendation}
                disabled={loading}
                className="mt-5 w-full rounded-xl bg-green-600 px-5 py-3 font-semibold text-white transition hover:bg-green-500 disabled:cursor-not-allowed disabled:bg-slate-700"
              >
                {loading ? "Booking..." : "Confirm Booking"}
              </button>
            )}
          </section>
        )}
        {booking && (
          <section className="mt-8 rounded-2xl border border-green-500/30 bg-green-500/10 p-6">
            <div className="flex items-center gap-3">
              <span className="text-3xl">✅</span>

              <div>
                <h2 className="text-2xl font-bold">
                  Booking Confirmed
                </h2>

                <p className="text-slate-300">
                  Your flight and hotel have been successfully booked.
                </p>
              </div>
            </div>

            <div className="mt-5 grid gap-3 rounded-xl bg-slate-900 p-4">
              <div>
                <p className="text-sm text-slate-400">Booking ID</p>
                <p className="font-semibold">{booking.booking_id}</p>
              </div>

              <div>
                <p className="text-sm text-slate-400">Flight</p>
                <p className="font-semibold">{booking.selected_flight_id}</p>
              </div>

              <div>
                <p className="text-sm text-slate-400">Hotel</p>
                <p className="font-semibold">{booking.selected_hotel_id}</p>
              </div>

              <div>
                <p className="text-sm text-slate-400">Total</p>
                <p className="text-xl font-bold">
                  {booking.currency} {booking.total_price.toFixed(2)}
                </p>
              </div>

              <div>
                <p className="text-sm text-slate-400">Status</p>
                <p className="font-semibold text-green-400">
                  {booking.status}
                </p>
              </div>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}