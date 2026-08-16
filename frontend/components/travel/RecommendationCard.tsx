import type { Recommendation } from "./types";

type RecommendationCardProps = {
  recommendation: Recommendation;
  index: number;
  selected: boolean;
  loading: boolean;
  onSelect: (recommendation: Recommendation) => void;
};

function formatDuration(minutes: number) {
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return remainingMinutes === 0 ? `${hours}h` : `${hours}h ${remainingMinutes}m`;
}

function formatDate(date: string) {
  try {
    return new Intl.DateTimeFormat("en", {
      month: "short",
      day: "numeric",
      year: "numeric",
    }).format(new Date(`${date}T00:00:00`));
  } catch {
    return date;
  }
}

export default function RecommendationCard({
  recommendation,
  index,
  selected,
  loading,
  onSelect,
}: RecommendationCardProps) {
  const { flight, hotel } = recommendation;

  // Convert score to percentage representation
  const matchPercentage = Math.round(recommendation.score * 100);

  return (
    <article
      className={`group overflow-hidden rounded-xl border bg-card text-foreground transition-all duration-200 ${
        selected
          ? "border-primary ring-1 ring-primary shadow-sm"
          : "border-border hover:border-ring/45 hover:shadow-sm"
      }`}
    >
      {/* Card Header */}
      <div className="flex items-center justify-between border-b border-border bg-muted/20 px-5 py-3">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
            Option {index + 1}
          </span>
          <span className="inline-flex items-center rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium text-emerald-600 dark:text-emerald-400">
            {matchPercentage}% Match
          </span>
        </div>

        <div className="text-right">
          <p className="text-[10px] text-muted-foreground">Total Combined Cost</p>
          <p className="text-base font-bold tracking-tight">
            {recommendation.total_price.toFixed(2)}{" "}
            <span className="text-xs font-normal text-muted-foreground">
              {flight.currency}
            </span>
          </p>
        </div>
      </div>

      {/* Flight Detail */}
      <div className="px-5 py-4 border-b border-border bg-card">
        <div className="mb-3 flex items-center justify-between">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
            Flight
          </span>
          <span className="text-xs text-muted-foreground">
            {flight.direct ? "Direct" : "Non-direct"}
            <span className="mx-1.5 opacity-40">·</span>
            {formatDuration(flight.duration_minutes)}
          </span>
        </div>

        <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-4 py-1">
          <div>
            <p className="text-base font-bold tracking-tight">{flight.origin}</p>
            <p className="text-xs text-muted-foreground">{formatDate(flight.departure_date)}</p>
          </div>

          <div className="flex flex-col items-center gap-1 text-muted-foreground">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="opacity-50"
            >
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </div>

          <div className="text-right">
            <p className="text-base font-bold tracking-tight">{flight.destination}</p>
            <p className="text-xs text-muted-foreground">{formatDate(flight.return_date)}</p>
          </div>
        </div>

        <div className="mt-2.5 flex items-center justify-between text-xs text-muted-foreground">
          <span>{flight.airline}</span>
          <span className="font-medium text-foreground">
            {flight.price.toFixed(2)} {flight.currency}
          </span>
        </div>
      </div>

      {/* Hotel Detail */}
      <div className="px-5 py-4 bg-card">
        <div className="mb-3 flex items-center justify-between">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
            Hotel
          </span>
          <div className="flex items-center gap-1 text-xs">
            <svg
              className="h-3 w-3 text-amber-500 fill-amber-500"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            <span className="font-medium">{hotel.rating.toFixed(1)} / 5</span>
          </div>
        </div>

        <div>
          <p className="text-sm font-semibold tracking-tight">{hotel.name}</p>
          <p className="text-xs text-muted-foreground mt-0.5">{hotel.destination}</p>
        </div>

        <div className="mt-2.5 flex items-center justify-between text-xs text-muted-foreground">
          <span>{hotel.price_per_night.toFixed(2)} {hotel.currency} / night</span>
          <span className="font-medium text-foreground">
            {hotel.total_price.toFixed(2)} {hotel.currency}
          </span>
        </div>
      </div>

      {/* Select Action Area */}
      <div className="border-t border-border bg-muted/10 px-5 py-3.5 flex justify-end">
        <button
          type="button"
          onClick={() => onSelect(recommendation)}
          disabled={loading}
          className={`w-full sm:w-auto rounded-lg px-4 py-2 text-xs font-semibold transition-all duration-200 focus:outline-none focus:ring-1 focus:ring-ring ${
            selected
              ? "bg-secondary text-secondary-foreground border border-border cursor-default"
              : "bg-primary text-primary-foreground hover:opacity-90 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
          }`}
        >
          {loading && selected ? (
            <span className="flex items-center gap-1.5 justify-center">
              <svg className="animate-spin h-3 w-3" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Selecting...
            </span>
          ) : selected ? (
            <span className="flex items-center gap-1 justify-center">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              Selected
            </span>
          ) : (
            "Select this option"
          )}
        </button>
      </div>
    </article>
  );
}