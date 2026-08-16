import type { Recommendation, TravelApproval } from "../travel/types";
import TripSummary from "../travel/TripSummary";

type ApprovalPanelProps = {
  approval: TravelApproval;
  recommendation: Recommendation;
  loading: boolean;
  onApprove: () => void;
  onReject: () => void;
  onBook: () => void;
};

export default function ApprovalPanel({
  approval,
  recommendation,
  loading,
  onApprove,
  onReject,
  onBook,
}: ApprovalPanelProps) {
  const isPending = approval.status === "pending";
  const isApproved = approval.status === "approved";

  return (
    <section className="flex h-full min-h-0 flex-col bg-background">
      {/* Header */}
      <header className="shrink-0 border-b border-border bg-background px-6 py-4">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              Review Step
            </p>
            <h2 className="text-base font-semibold tracking-tight text-foreground">
              Trip Verification
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Confirm all details are correct before approving this booking.
            </p>
          </div>

          <div>
            {isPending ? (
              <span className="inline-flex items-center rounded-full bg-amber-500/10 px-2.5 py-0.5 text-xs font-medium text-amber-600 dark:text-amber-400 border border-amber-500/20 shadow-sm animate-pulse">
                Pending Approval
              </span>
            ) : isApproved ? (
              <span className="inline-flex items-center rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-medium text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 shadow-sm">
                Approved
              </span>
            ) : (
              <span className="inline-flex items-center rounded-full bg-red-500/10 px-2.5 py-0.5 text-xs font-medium text-red-600 dark:text-red-400 border border-red-500/20 shadow-sm">
                Rejected
              </span>
            )}
          </div>
        </div>
      </header>

      {/* Main Review Area */}
      <div className="flex-1 overflow-y-auto px-6 py-6 bg-background">
        <div className="mx-auto max-w-xl space-y-6">
          
          {/* Trip Summary Details */}
          <TripSummary recommendation={recommendation} />

          {/* Action Cards */}
          <div className="rounded-xl border border-border bg-card p-5 space-y-4 shadow-sm">
            <div className="flex items-start gap-3 text-muted-foreground">
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="mt-0.5 shrink-0"
              >
                <circle cx="12" cy="12" r="10" />
                <path d="M12 16v-4" />
                <path d="M12 8h.01" />
              </svg>
              <p className="text-xs leading-relaxed">
                Note: This is a demonstration environment. Confirming approval will simulate a booking, but no actual ticket issuance or hotel reservations will be made, and your payment method will not be charged.
              </p>
            </div>

            {isPending && (
              <div className="grid grid-cols-2 gap-3 pt-2">
                <button
                  type="button"
                  onClick={onReject}
                  disabled={loading}
                  className="rounded-lg border border-border bg-card px-4 py-2.5 text-xs font-semibold text-foreground transition-all duration-200 hover:bg-muted focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Change option
                </button>

                <button
                  type="button"
                  onClick={onApprove}
                  disabled={loading}
                  className="rounded-lg bg-primary text-primary-foreground px-4 py-2.5 text-xs font-semibold transition-all duration-200 hover:opacity-90 focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-1.5">
                      <svg className="animate-spin h-3.5 w-3.5" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Approving...
                    </span>
                  ) : (
                    "Approve trip"
                  )}
                </button>
              </div>
            )}

            {isApproved && (
              <div className="pt-2">
                <button
                  type="button"
                  onClick={onBook}
                  disabled={loading}
                  className="w-full rounded-lg bg-emerald-600 text-white px-4 py-2.5 text-xs font-semibold transition-all duration-200 hover:bg-emerald-700 active:scale-[0.99] focus:outline-none focus:ring-1 focus:ring-emerald-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-1.5">
                      <svg className="animate-spin h-3.5 w-3.5" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Confirming booking...
                    </span>
                  ) : (
                    "Confirm booking"
                  )}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}