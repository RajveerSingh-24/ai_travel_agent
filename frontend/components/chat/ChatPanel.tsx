import type { Message } from "../travel/types";
import MessageList from "./MessageList";
import ChatInput from "./ChatInput";

type ChatPanelProps = {
  messages: Message[];
  input: string;
  loading: boolean;
  onInputChange: (value: string) => void;
  onSend: () => void;
};

export default function ChatPanel({
  messages,
  input,
  loading,
  onInputChange,
  onSend,
}: ChatPanelProps) {
  return (
    <section className="flex h-full min-h-0 flex-col bg-background">
      <div className="flex h-14 shrink-0 items-center justify-between border-b border-border px-5 bg-background">
        <div className="flex items-center gap-2">
          <div className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </div>
          <div>
            <h2 className="text-sm font-semibold tracking-tight text-foreground">
              Travel Assistant
            </h2>
            <p className="text-[10px] text-muted-foreground">
              AI Planner Active
            </p>
          </div>
        </div>
      </div>

      <MessageList messages={messages} loading={loading} />

      <ChatInput
        value={input}
        loading={loading}
        onChange={onInputChange}
        onSend={onSend}
      />
    </section>
  );
}