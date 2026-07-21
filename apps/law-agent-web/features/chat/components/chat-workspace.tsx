"use client";

import { FormEvent, useState } from "react";

import type { DemoRunResponse } from "@/lib/api/client";

export interface ChatWorkspaceProps {
  executeRun: (query: string) => Promise<DemoRunResponse>;
}

export function ChatWorkspace({ executeRun }: ChatWorkspaceProps) {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<DemoRunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalized = query.trim();
    if (!normalized || pending) return;

    setPending(true);
    setError(null);
    try {
      setResult(await executeRun(normalized));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unexpected error");
    } finally {
      setPending(false);
    }
  }

  return (
    <section className="card stack" aria-labelledby="chat-heading">
      <div>
        <h1 id="chat-heading">Enterprise AI Agent</h1>
        <p className="meta">Foundation skeleton: parallel LangGraph demo execution.</p>
      </div>
      <form className="stack" onSubmit={submit}>
        <label htmlFor="question">Question</label>
        <textarea
          id="question"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Ask a question..."
        />
        <button type="submit" disabled={pending || query.trim().length === 0}>
          {pending ? "Running…" : "Send"}
        </button>
      </form>
      <div aria-live="polite">
        {result ? (
          <div className="answer">
            <p>{result.final_answer}</p>
            <p className="meta">Evidence items: {result.evidence_count}</p>
          </div>
        ) : null}
        {error ? <p className="error">{error}</p> : null}
      </div>
    </section>
  );
}
