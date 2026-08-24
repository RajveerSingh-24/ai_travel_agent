"use client";

import React, { useState } from "react";
import type { TripSession } from "../../app/page";

interface BookingHistoryViewProps {
  sessions: TripSession[];
}

export default function BookingHistoryView({ sessions }: BookingHistoryViewProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const bookedSessions = sessions.filter(
    (s) => s.booking && s.booking.status === "confirmed" && s.selectedRecommendation
  );

  return (
    <div className="flex-1 h-full flex flex-col bg-background animate-in fade-in duration-300">
      <div className="flex items-center justify-between p-6 border-b border-border bg-card/50">
        <div>
          <h2 className="text-2xl font-bold text-foreground tracking-tight">
            My Bookings
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            View and manage your past confirmed travel bookings
          </p>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto">
          {bookedSessions.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-center text-muted-foreground bg-muted/20 rounded-xl border border-dashed border-border">
              <svg className="w-16 h-16 mb-4 opacity-20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20" />
              </svg>
              <p className="text-lg font-medium text-foreground">No bookings found</p>
              <p className="text-sm mt-1">Your confirmed bookings will appear here.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {bookedSessions.map((session) => {
                const booking = session.booking!;
                const rec = session.selectedRecommendation!;
                const date = new Date(session.createdAt).toLocaleDateString(undefined, {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                });
                
                const isExpanded = expandedId === session.id;

                return (
                  <div
                    key={session.id}
                    className={`border rounded-xl overflow-hidden transition-all duration-200 cursor-pointer ${
                      isExpanded 
                        ? "border-emerald-500/30 bg-card shadow-md" 
                        : "border-border bg-card hover:border-muted-foreground/30 hover:bg-muted/10 shadow-sm"
                    }`}
                    onClick={() => setExpandedId(isExpanded ? null : session.id)}
                  >
                    <div className="flex items-center justify-between p-5">
                      <div className="flex items-center gap-4">
                        <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl transition-colors ${isExpanded ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400" : "bg-muted text-muted-foreground"}`}>
                          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                            <polyline points="22 4 12 14.01 9 11.01" />
                          </svg>
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-foreground">
                            {session.title.replace("Trip to ", "")}
                          </h3>
                          <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
                            <span>Booked on {date}</span>
                            <span>&bull;</span>
                            <span className="font-mono text-[11px] bg-muted px-2 py-0.5 rounded text-foreground">
                              Ref: {booking.booking_id.substring(0, 8)}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-6">
                        <div className="text-right">
                          <p className="text-lg font-bold text-foreground">
                            {booking.currency} {booking.total_price.toLocaleString()}
                          </p>
                          <span className="inline-flex items-center rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-[11px] font-medium text-emerald-600 dark:text-emerald-400 mt-1">
                            Confirmed
                          </span>
                        </div>
                        <div className={`text-muted-foreground transition-transform duration-200 ${isExpanded ? "rotate-180" : ""}`}>
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <polyline points="6 9 12 15 18 9" />
                          </svg>
                        </div>
                      </div>
                    </div>
                    
                    {isExpanded && (
                      <div className="p-5 border-t border-border bg-muted/5 flex flex-col gap-6 animate-in slide-in-from-top-2 duration-200">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          {/* Flight Details */}
                          <div className="space-y-3 bg-card p-4 rounded-lg border border-border">
                            <div className="flex items-center gap-2 text-sm font-bold text-foreground uppercase tracking-wider">
                              <div className="p-1.5 rounded-md bg-blue-500/10 text-blue-500">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                  <path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21.5 4c0 0-2 .5-3.5 2L14.5 9.5 6.3 7.7 4 8.7l5.2 4.4-4 4L2 19l4.1-1.1 4-4 4.4 5.2 1-2.3z" />
                                </svg>
                              </div>
                              Flight Details
                            </div>
                            <div className="space-y-2 text-sm mt-3">
                              <div className="flex justify-between">
                                <span className="text-muted-foreground">Airline</span>
                                <span className="font-medium text-foreground">{rec.flight.airline}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-muted-foreground">Route</span>
                                <span className="font-medium text-foreground">{rec.flight.origin} &rarr; {rec.flight.destination}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-muted-foreground">Dates</span>
                                <span className="font-medium text-foreground">{rec.flight.departure_date} to {rec.flight.return_date}</span>
                              </div>
                              <div className="flex justify-between pt-2 border-t border-border mt-2">
                                <span className="text-muted-foreground">Flight Price</span>
                                <span className="font-medium text-foreground">{rec.flight.currency} {rec.flight.price.toLocaleString()}</span>
                              </div>
                            </div>
                          </div>
                          {/* Hotel Details */}
                          <div className="space-y-3 bg-card p-4 rounded-lg border border-border">
                            <div className="flex items-center gap-2 text-sm font-bold text-foreground uppercase tracking-wider">
                              <div className="p-1.5 rounded-md bg-orange-500/10 text-orange-500">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                                  <polyline points="9 22 9 12 15 12 15 22" />
                                </svg>
                              </div>
                              Accommodation
                            </div>
                            <div className="space-y-2 text-sm mt-3">
                              <div className="flex justify-between">
                                <span className="text-muted-foreground">Hotel</span>
                                <span className="font-medium text-foreground">{rec.hotel.name}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-muted-foreground">Location</span>
                                <span className="font-medium text-foreground">{rec.hotel.destination}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-muted-foreground">Rating</span>
                                <span className="font-medium text-foreground flex items-center gap-1">
                                  <svg className="w-3.5 h-3.5 text-yellow-500 fill-yellow-500" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                                  </svg>
                                  {rec.hotel.rating} stars
                                </span>
                              </div>
                              <div className="flex justify-between pt-2 border-t border-border mt-2">
                                <span className="text-muted-foreground">Hotel Price</span>
                                <span className="font-medium text-foreground">{rec.hotel.currency} {rec.hotel.total_price.toLocaleString()}</span>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Receipt Details */}
                        <div className="bg-card p-5 rounded-lg border border-border">
                          <div className="flex items-center gap-2 text-sm font-bold text-foreground uppercase tracking-wider mb-4">
                            <div className="p-1.5 rounded-md bg-emerald-500/10 text-emerald-500">
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
                                <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
                                <line x1="9" y1="14" x2="15" y2="14" />
                                <line x1="9" y1="18" x2="15" y2="18" />
                                <line x1="9" y1="10" x2="9.01" y2="10" />
                              </svg>
                            </div>
                            Booking Receipt
                          </div>
                          
                          <div className="space-y-3 text-sm">
                            <div className="flex justify-between items-center text-muted-foreground">
                              <span>Flight ({rec.flight.origin} &rarr; {rec.flight.destination})</span>
                              <span className="font-mono text-foreground">{rec.flight.currency} {rec.flight.price.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between items-center text-muted-foreground">
                              <span>Accommodation ({rec.hotel.name})</span>
                              <span className="font-mono text-foreground">{rec.hotel.currency} {rec.hotel.total_price.toLocaleString()}</span>
                            </div>
                            <div className="pt-3 border-t border-dashed border-border flex justify-between items-center mt-2">
                              <span className="font-bold text-foreground">Total Amount Paid</span>
                              <span className="font-mono text-lg font-bold text-emerald-600 dark:text-emerald-400">
                                {booking.currency} {booking.total_price.toLocaleString()}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
