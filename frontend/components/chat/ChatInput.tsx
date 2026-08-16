type ChatInputProps = {
  value: string;
  loading: boolean;
  onChange: (value: string) => void;
  onSend: () => void;
};

export default function ChatInput({
  value,
  loading,
  onChange,
  onSend,
}: ChatInputProps) {
  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLInputElement>
  ) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      onSend();
    }
  };

  return (
    <div className="border-t border-border bg-background px-5 py-4 shrink-0">
      <div className="mx-auto flex max-w-2xl items-center gap-3 rounded-xl border border-border bg-card px-4 py-1.5 transition-all duration-200 focus-within:border-ring focus-within:ring-1 focus-within:ring-ring">
        <input
          type="text"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
          placeholder="Ask a question or enter details about your trip..."
          className="min-w-0 flex-1 bg-transparent py-2 text-sm text-foreground outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed"
        />

        <button
          type="button"
          onClick={onSend}
          disabled={loading || !value.trim()}
          aria-label="Send message"
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground transition-all duration-200 hover:opacity-90 disabled:cursor-not-allowed disabled:bg-muted disabled:text-muted-foreground"
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 16 16"
            fill="none"
            aria-hidden="true"
          >
            <path
              d="M3 8h9M8.5 4.5 12 8l-3.5 3.5"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>

      <p className="mt-2 text-center text-[10px] text-muted-foreground font-mono">
        Press Enter to send
      </p>
    </div>
  );
}