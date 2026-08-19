"use client";

import { useState, useEffect, MouseEvent } from "react";


export type TripSession = {
  id: string;
  title: string;
  messages: Message[];
  recommendations: Recommendation[] | null;
  selectedRecommendation: Recommendation | null;
  pendingApproval: TravelApproval | null;
  booking: BookingResult | null;
  createdAt: number;
};

import ThemeToggle from "../components/ui/ThemeToggle";
import ChatPanel from "../components/chat/ChatPanel";
import RecommendationPanel from "../components/travel/RecommendationPanel";
import ApprovalPanel from "../components/booking/ApprovalPanel";
import BookingConfirmation from "../components/booking/BookingConfirmation";
import Image from "next/image";
import type {
  Message,
  Recommendation,
  TravelApproval,
  BookingResult,
  TravelPlanResponse,
} from "../components/travel/types";

export default function Home() {
  const [sessions, setSessions] = useState<TripSession[]>([]);
  const [sessionId, setSessionId] = useState("");

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<Recommendation[] | null>(null);
  const [selectedRecommendation, setSelectedRecommendation] = useState<Recommendation | null>(null);
  const [pendingApproval, setPendingApproval] = useState<TravelApproval | null>(null);
  const [booking, setBooking] = useState<BookingResult | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const createNewTrip = () => {
    const newId = `frontend-${crypto.randomUUID()}`;
    const newSession: TripSession = {
      id: newId,
      title: "New Trip",
      messages: [
        {
          role: "assistant",
          content: "Tell me where you'd like to go, when you're travelling, and who's coming along. I'll take care of the planning.",
        },
      ],
      recommendations: null,
      selectedRecommendation: null,
      pendingApproval: null,
      booking: null,
      createdAt: Date.now(),
    };
    setSessions((prev) => [newSession, ...prev]);
    loadSession(newSession);
  };

  const loadSession = (session: TripSession) => {
    setSessionId(session.id);
    setMessages(session.messages);
    setRecommendations(session.recommendations);
    setSelectedRecommendation(session.selectedRecommendation);
    setPendingApproval(session.pendingApproval);
    setBooking(session.booking);
  };

  const deleteSession = (e: MouseEvent, idToDelete: string) => {
    e.stopPropagation();
    setSessions((prev) => {
      const filtered = prev.filter((s) => s.id !== idToDelete);
      localStorage.setItem("travel-agent-sessions", JSON.stringify(filtered));
      if (sessionId === idToDelete) {
        if (filtered.length > 0) {
          setTimeout(() => loadSession(filtered[0]), 0);
        } else {
          setTimeout(() => createNewTrip(), 0);
        }
      }
      return filtered;
    });
  };

  // Initialize from local storage on mount
  useEffect(() => {
    const stored = localStorage.getItem("travel-agent-sessions");
    let loadedSessions: TripSession[] = [];
    if (stored) {
      try {
        loadedSessions = JSON.parse(stored);
      } catch {}
    }
    if (loadedSessions.length > 0) {
      setSessions(loadedSessions);
      loadSession(loadedSessions[0]);
    } else {
      createNewTrip();
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Sync state changes to active session
  useEffect(() => {
    if (!sessionId) return;
    setSessions((prev) => {
      const sessionIndex = prev.findIndex((s) => s.id === sessionId);
      if (sessionIndex === -1) return prev;
      const existing = prev[sessionIndex];
      const updatedSession: TripSession = {
        ...existing,
        messages,
        recommendations,
        selectedRecommendation,
        pendingApproval,
        booking,
      };
      const newSessions = [...prev];
      newSessions[sessionIndex] = updatedSession;
      localStorage.setItem("travel-agent-sessions", JSON.stringify(newSessions));
      return newSessions;
    });
  }, [sessionId, messages, recommendations, selectedRecommendation, pendingApproval, booking]);

  const hasWorkspace =
    recommendations !== null || selectedRecommendation !== null || booking !== null;

  const sendMessage = async () => {
    const message = input.trim();

    if (!message || loading) {
      return;
    }

    setInput("");
    setLoading(true);

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: message,
      },
    ]);

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
            message,
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

      // Update session title dynamically based on destination
      if (data.constraints?.destination) {
        setSessions((prev) => {
          const destTitle = `Trip to ${data.constraints!.destination}`;
          const updated = prev.map((s) =>
            s.id === sessionId && s.title !== destTitle
              ? { ...s, title: destTitle }
              : s
          );
          localStorage.setItem("travel-agent-sessions", JSON.stringify(updated));
          return updated;
        });
      }

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
              "I found some options that match your trip. You can review them alongside our conversation.",
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

  const selectRecommendation = async (
    recommendation: Recommendation
  ) => {
    if (loading) {
      return;
    }

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
            message: [...messages].reverse().find(m => m.role === "user")?.content || "Plan my trip",
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
    if (!pendingApproval || loading) {
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
            "Your trip has been approved. I can now proceed with the booking.",
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
    if (!pendingApproval || loading) {
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
      setSelectedRecommendation(null);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "No problem. Let's look at the other options.",
        },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            error instanceof Error
              ? `Sorry, I couldn't change the selection: ${error.message}`
              : "Sorry, I couldn't change the selection.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const bookRecommendation = async () => {
    if (
      !pendingApproval ||
      pendingApproval.status !== "approved" ||
      loading
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
          content:
            "Your trip has been booked successfully. The booking details are shown alongside our conversation.",
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

  const startNewTrip = () => {
    createNewTrip();
  };

  return (
    <main className="h-screen overflow-hidden bg-background text-foreground">
      <div className="flex h-full flex-col">
        {/* Application header */}
        <header className="flex h-16 shrink-0 items-center justify-between border-b border-border bg-card/85 backdrop-blur-md px-6 sticky top-0 z-50 transition-all duration-200">
          <div className="flex items-center gap-3.5">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center">
                <Image
                  src="/TRAVEL.png"
                  alt="AI Travel Agent"
                  width={36}
                  height={36}
                  priority
                />
              </div>

            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-sm font-bold tracking-tight text-foreground leading-none">
                  AI Travel Agent
                </h1>
                <span className="inline-flex items-center rounded-md bg-emerald-500/10 px-1.5 py-0.5 text-[9px] font-medium text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                  Agent v1.0
                </span>
              </div>

              <p className="text-[10px] text-muted-foreground mt-1 leading-none font-medium">
                Intelligent trip planning workspace
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            {hasWorkspace && (
              <button
                type="button"
                onClick={startNewTrip}
                className="lg:hidden flex items-center gap-1.5 rounded-lg border border-border bg-card px-3 py-1.5 text-xs font-semibold text-foreground transition-all duration-200 hover:bg-muted hover:text-foreground active:scale-[0.98] shadow-sm"
              >
                <svg
                  width="11"
                  height="11"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <line x1="12" y1="5" x2="12" y2="19" />
                  <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
                New trip
              </button>
            )}

            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="hidden lg:flex items-center justify-center h-9 w-9 rounded-md border border-border bg-background hover:bg-muted text-muted-foreground transition-colors"
              title="Toggle sidebar"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <line x1="9" y1="3" x2="9" y2="21" />
              </svg>
            </button>

            <ThemeToggle />
          </div>
        </header>

        {/* Main layout wrapper */}
        <div className="flex flex-1 min-h-0 overflow-hidden">
          {/* Sidebar */}
          <aside className={`hidden lg:flex flex-col shrink-0 border-border bg-card transition-all duration-300 ${isSidebarOpen ? "w-64 border-r" : "w-0 overflow-hidden border-r-0"}`}>
            <div className="p-4 shrink-0 w-64">
              <button
                type="button"
                onClick={startNewTrip}
                className="w-full flex items-center justify-between gap-1.5 rounded-lg border border-border bg-background px-3.5 py-2 text-xs font-semibold text-foreground transition-all duration-200 hover:bg-muted active:scale-[0.98] shadow-sm"
              >
                <span className="flex items-center gap-1.5">
                  <svg
                    width="12"
                    height="12"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <line x1="12" y1="5" x2="12" y2="19" />
                    <line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                  New trip
                </span>
                <span className="text-[10px] font-mono text-muted-foreground border border-border rounded px-1 py-0.5 leading-none">
                  ⌘N
                </span>
              </button>
            </div>

            <div className="flex-1 overflow-y-auto px-3 py-2 space-y-4 w-64">
              <div>
                <h3 className="px-2 text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                  History
                </h3>
                <div className="mt-1.5 space-y-1">
                  {sessions.map((session) => (
                    <div
                      key={session.id}
                      className={`group relative flex items-center justify-between rounded-lg px-2.5 py-2 text-xs transition ${
                        sessionId === session.id
                          ? "bg-muted font-semibold text-foreground border border-border shadow-sm"
                          : "text-muted-foreground hover:bg-muted/50 hover:text-foreground border border-transparent"
                      }`}
                    >
                      <button
                        onClick={() => loadSession(session)}
                        className="flex-1 text-left flex items-center gap-2 truncate pr-6 focus:outline-none"
                      >
                        {sessionId === session.id ? (
                          <span className="relative flex h-1.5 w-1.5 shrink-0 ml-1 mr-0.5">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
                          </span>
                        ) : (
                          <svg className="h-3.5 w-3.5 opacity-65 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                          </svg>
                        )}
                        <span className="truncate">{session.title}</span>
                      </button>
                      
                      <button
                        onClick={(e) => deleteSession(e, session.id)}
                        title="Delete conversation"
                        className={`absolute right-2 p-1 rounded hover:bg-muted-foreground/15 text-muted-foreground hover:text-red-500 transition duration-150 ${
                          sessionId === session.id ? "opacity-100" : "opacity-0 group-hover:opacity-100 focus:opacity-100"
                        }`}
                      >
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Profile footer */}
            <div className="shrink-0 border-t border-border p-4 bg-muted/10 w-64">
              <div className="flex items-center gap-3">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-muted text-[10px] font-bold text-foreground border border-border">
                  U
                </div>
                <div>
                  <p className="text-xs font-semibold text-foreground leading-none">
                    Rajveer Singh
                  </p>
                  <p className="text-[10px] text-muted-foreground mt-1 leading-none">
                    Session Active
                  </p>
                </div>
              </div>
            </div>
          </aside>

          {/* Main workspace */}
          <div className="min-h-0 flex-1 flex flex-col h-full bg-background">
            {!hasWorkspace ? (
              /*
               * Initial state:
               * The conversation gets the entire workspace.
               */
              <ChatPanel
                messages={messages}
                input={input}
                loading={loading}
                onInputChange={setInput}
                onSend={sendMessage}
              />
            ) : (
              /*
               * Planning state:
               * Conversation remains available on the left while
               * travel options / approval / booking occupy the right.
               */
              <div className="grid h-full min-h-0 grid-cols-1 lg:grid-cols-[minmax(380px,0.85fr)_minmax(520px,1.15fr)]">
                <div className="min-h-0 border-b border-border bg-background lg:border-b-0 lg:border-r">
                  <ChatPanel
                    messages={messages}
                    input={input}
                    loading={loading}
                    onInputChange={setInput}
                    onSend={sendMessage}
                  />
                </div>

                <div className="min-h-0 bg-background">
                  {booking ? (
                    <BookingConfirmation
                      booking={booking}
                      recommendation={selectedRecommendation}
                      onNewTrip={startNewTrip}
                    />
                  ) : pendingApproval && selectedRecommendation ? (
                    <ApprovalPanel
                      approval={pendingApproval}
                      recommendation={selectedRecommendation}
                      loading={loading}
                      onApprove={approveRecommendation}
                      onReject={rejectRecommendation}
                      onBook={bookRecommendation}
                    />
                  ) : (
                    <RecommendationPanel
                      recommendations={recommendations ?? []}
                      selectedRecommendation={selectedRecommendation}
                      loading={loading}
                      onSelect={selectRecommendation}
                    />
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}