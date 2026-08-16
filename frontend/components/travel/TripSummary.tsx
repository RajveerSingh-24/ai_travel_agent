import type { Recommendation } from "./types";

type TripSummaryProps = {
  recommendation: Recommendation;
};

function formatDuration(minutes: number) {
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return remainingMinutes === 0 ? `${hours}h` : `${hours}h ${remainingMinutes}m`;
}

function formatDate(dateString: string) {
  try {
    return new Intl.DateTimeFormat("en", {
      month: "short",
      day: "numeric",
      year: "numeric",
    }).format(new Date(`${dateString}T00:00:00`));
  } catch {
    return dateString;
  }
}

export default function TripSummary({ recommendation }: TripSummaryProps) {
  const { flight, hotel } = recommendation;

  return (
    <div className="space-y-4 rounded-xl border border-border bg-card p-5 text-foreground shadow-sm">
      {/* Flight Section */}
      <div>
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Flight Details
          </h3>
          <span className="inline-flex items-center rounded-full bg-accent px-2 py-0.5 text-xs font-medium text-foreground">
            {flight.direct ? "Direct" : "Non-direct"}
            <span className="mx-1.5 opacity-40">·</span>
            {formatDuration(flight.duration_minutes)}
          </span>
        </div>

        <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-4 py-2">
          <div>
            <p className="text-base font-bold tracking-tight">{flight.origin}</p>
            <p className="text-xs text-muted-foreground">{formatDate(flight.departure_date)}</p>
          </div>

          <div className="flex flex-col items-center gap-1 text-muted-foreground">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="opacity-60"
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

        <div className="mt-2 flex justify-between text-xs text-muted-foreground">
          <span>{flight.airline}</span>
          <span>
            {flight.price.toFixed(2)} {flight.currency}
          </span>
        </div>
      </div>

      <hr className="border-border" />

      {/* Hotel Section */}
      <div>
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Hotel Details
          </h3>
          <div className="flex items-center gap-1">
            <svg
              className="h-3 w-3 text-amber-500 fill-amber-500"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            <span className="text-xs font-medium">{hotel.rating.toFixed(1)} / 5</span>
          </div>
        </div>

        <div>
          <p className="text-base font-bold tracking-tight">{hotel.name}</p>
          <p className="text-xs text-muted-foreground">{hotel.destination}</p>
        </div>

        <div className="mt-2 flex justify-between text-xs text-muted-foreground">
          <span>{hotel.price_per_night.toFixed(2)} {hotel.currency} / night</span>
          <span>
            {hotel.total_price.toFixed(2)} {hotel.currency}
          </span>
        </div>
      </div>

      <hr className="border-border" />

      {/* Summary Footer */}
      <div className="flex items-center justify-between pt-1">
        <span className="text-sm font-medium text-muted-foreground">Total Combined Cost</span>
        <span className="text-lg font-bold tracking-tight text-foreground">
          {recommendation.total_price.toFixed(2)} {flight.currency}
        </span>
      </div>
    </div>
  );
}
