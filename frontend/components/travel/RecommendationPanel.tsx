import type { Recommendation } from "./types";
import RecommendationCard from "./RecommendationCard";

type RecommendationPanelProps = {
  recommendations: Recommendation[];
  selectedRecommendation: Recommendation | null;
  loading: boolean;
  onSelect: (recommendation: Recommendation) => void;
};

export default function RecommendationPanel({
  recommendations,
  selectedRecommendation,
  loading,
  onSelect,
}: RecommendationPanelProps) {
  if (recommendations.length === 0) {
    return (
      <section className="flex h-full min-h-0 flex-col bg-background">
        <div className="flex flex-1 flex-col items-center justify-center px-8 py-12 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl border border-border bg-card text-muted-foreground shadow-sm">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="12" cy="12" r="10" />
              <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20" />
              <path d="M2 12h20" />
            </svg>
          </div>
          <h3 className="mt-4 text-sm font-semibold text-foreground">
            Travel recommendations workspace
          </h3>
          <p className="mt-2 max-w-xs text-xs text-muted-foreground leading-relaxed">
            Your flight and hotel options will appear here once you share your travel dates, destination, and preferences with the assistant.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="flex h-full min-h-0 flex-col bg-background">
      <header className="shrink-0 border-b border-border bg-background px-6 py-4">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              Workspace
            </p>
            <h2 className="text-base font-semibold tracking-tight text-foreground">
              Recommended Options
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Compare flight and hotel combinations matching your request.
            </p>
          </div>

          <span className="shrink-0 inline-flex items-center rounded-full border border-border bg-secondary px-2.5 py-0.5 text-xs font-medium text-secondary-foreground shadow-sm">
            {recommendations.length}{" "}
            {recommendations.length === 1 ? "option" : "options"}
          </span>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="mx-auto flex max-w-2xl flex-col gap-5">
          {recommendations.map((recommendation, index) => (
            <RecommendationCard
              key={`${recommendation.flight.id}-${recommendation.hotel.id}`}
              recommendation={recommendation}
              index={index}
              selected={
                selectedRecommendation?.flight.id ===
                  recommendation.flight.id &&
                selectedRecommendation?.hotel.id === recommendation.hotel.id
              }
              loading={loading}
              onSelect={onSelect}
            />
          ))}
        </div>
      </div>
    </section>
  );
}