import { useEffect, useState } from "react";
import type { Message } from "../travel/types";

type MessageListProps = {
  messages: Message[];
  loading: boolean;
};

function StreamedText({ content }: { content: string }) {
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    let currentLength = 0;
    
    const rFrame = requestAnimationFrame(() => {
      setDisplayedText("");
    });

    const interval = setInterval(() => {
      if (currentLength < content.length) {
        currentLength += 2; // Stream 2 characters per tick for a snappy, premium feel
        if (currentLength > content.length) {
          currentLength = content.length;
        }
        setDisplayedText(content.slice(0, currentLength));
      } else {
        clearInterval(interval);
      }
    }, 12);

    return () => {
      cancelAnimationFrame(rFrame);
      clearInterval(interval);
    };
  }, [content]);

  return (
    <>
      {displayedText.split("\n").map((line, lineIndex) => (
        <p key={lineIndex}>{line}</p>
      ))}
    </>
  );
}

export default function MessageList({
  messages,
  loading,
}: MessageListProps) {
  return (
    <div className="flex-1 overflow-y-auto bg-background px-5 py-8">
      <div className="mx-auto flex w-full max-w-2xl flex-col gap-6">
        {messages.map((message, index) => {
          const isUser = message.role === "user";

          return (
            <div
              key={index}
              className={`flex w-full ${
                isUser ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`flex max-w-[85%] gap-3.5 ${
                  isUser ? "flex-row-reverse" : "flex-row"
                }`}
              >
                {/* Assistant avatar */}
                {!isUser && (
                  <div className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-border bg-muted text-[10px] font-bold tracking-tight text-foreground shadow-sm">
                    AI
                  </div>
                )}

                <div
                  className={`min-w-0 ${
                    isUser
                      ? "rounded-2xl rounded-tr-xs bg-indigo-600 text-white border border-indigo-700/40 px-4 py-2.5 shadow-sm"
                      : "rounded-2xl rounded-tl-xs bg-card text-foreground border border-border px-4 py-2.5 shadow-sm"
                  }`}
                >
                  {/* Message */}
                  <div
                    className={`space-y-1.5 text-sm leading-relaxed ${
                      isUser
                        ? "text-white"
                        : "text-foreground"
                    }`}
                  >
                    {!isUser && index === messages.length - 1 ? (
                      <StreamedText content={message.content} />
                    ) : (
                      message.content.split("\n").map((line, lineIndex) => (
                        <p key={lineIndex}>{line}</p>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}

        {/* Loading indicator */}
        {loading && (
          <div className="flex w-full justify-start">
            <div className="flex gap-3.5 items-start">
              <div className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-border bg-muted text-[10px] font-bold tracking-tight text-foreground shadow-sm">
                AI
              </div>

              <div className="rounded-2xl rounded-tl-xs bg-card border border-border px-4 py-3 shadow-sm flex items-center justify-center min-h-[36px]">
                <div className="flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground opacity-60" />
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground opacity-60 [animation-delay:0.2s]" />
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground opacity-60 [animation-delay:0.4s]" />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}