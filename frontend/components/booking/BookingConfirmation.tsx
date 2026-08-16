import type { BookingResult, Recommendation } from "../travel/types";
import TripSummary from "../travel/TripSummary";

type BookingConfirmationProps = {
  booking: BookingResult;
  recommendation: Recommendation | null;
  onNewTrip: () => void;
};

function DetailRow({
  label,
  value,
  isMono = false,
}: {
  label: string;
  value: string;
  isMono?: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-4 py-3 border-b border-border/50 last:border-0">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className={`text-right text-xs font-semibold text-foreground ${isMono ? "font-mono tracking-tight" : ""}`}>
        {value}
      </span>
    </div>
  );
}

export default function BookingConfirmation({
  booking,
  recommendation,
  onNewTrip,
}: BookingConfirmationProps) {
  return (
    <section className="flex h-full min-h-0 flex-col bg-background">
      {/* Header */}
      <header className="shrink-0 border-b border-border bg-background px-6 py-4">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
            Process Complete
          </p>
          <h2 className="text-base font-semibold tracking-tight text-foreground">
            Trip Confirmation
          </h2>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-6 py-6 bg-background">
        <div className="mx-auto max-w-xl space-y-6">
          
          {/* Status Card */}
          <div className="rounded-xl border border-border bg-card p-6 text-center shadow-sm">
            {booking.status === "confirmed" ? (
              <>
                <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                  <svg
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </div>
                <h3 className="mt-3 text-sm font-semibold text-foreground">
                  Booking Successfully Confirmed
                </h3>
                <p className="mt-1.5 text-xs text-muted-foreground max-w-xs mx-auto leading-relaxed">
                  Your reservations have been processed. The receipt and trip details are shown below.
                </p>
              </>
            ) : (
              <>
                <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20">
                  <svg
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                </div>
                <h3 className="mt-3 text-sm font-semibold text-foreground">
                  Booking Failed
                </h3>
                <p className="mt-1.5 text-xs text-muted-foreground max-w-xs mx-auto leading-relaxed">
                  We could not process your reservations at this time. Please review your selection and try again.
                </p>
              </>
            )}
          </div>

          {/* Receipt Info */}
          <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
            <h4 className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground mb-3">
              Receipt Details
            </h4>
            <div className="divide-y divide-border">
              <DetailRow
                label="Booking reference"
                value={booking.booking_id}
                isMono
              />
              <DetailRow
                label="Status"
                value={booking.status.toUpperCase()}
              />
              <DetailRow
                label="Flight ID"
                value={booking.selected_flight_id}
                isMono
              />
              <DetailRow
                label="Hotel ID"
                value={booking.selected_hotel_id}
                isMono
              />
            </div>

            <div className="mt-4 pt-4 border-t border-border flex items-center justify-between">
              <span className="text-xs font-semibold text-muted-foreground">Total Charged</span>
              <span className="text-base font-bold tracking-tight text-foreground">
                {booking.total_price.toFixed(2)} {booking.currency}
              </span>
            </div>
          </div>

          {/* Trip Summary (if available) */}
          {recommendation && (
            <div className="space-y-2">
              <h4 className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground px-1">
                Itinerary Summary
              </h4>
              <TripSummary recommendation={recommendation} />
            </div>
          )}

          {/* Actions */}
          <div className="pt-2">
            <button
              type="button"
              onClick={onNewTrip}
              className="w-full rounded-lg bg-primary text-primary-foreground px-4 py-2.5 text-xs font-semibold transition-all duration-200 hover:opacity-90 active:scale-[0.99] focus:outline-none focus:ring-1 focus:ring-ring"
            >
              Plan another trip
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}