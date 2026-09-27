"use client";

import { FormEvent, useEffect, useState } from "react";
import type { Document, DocumentsResponse } from "@/lib/types";

type Filters = {
  q: string;
  published_from: string;
  published_to: string;
};

const emptyFilters: Filters = {
  q: "",
  published_from: "",
  published_to: "",
};

export default function HomePage() {
  const [draft, setDraft] = useState<Filters>(emptyFilters);
  const [applied, setApplied] = useState<Filters>(emptyFilters);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [total, setTotal] = useState(0);
  const [nextOffset, setNextOffset] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchDocuments(applied, 0);
        if (cancelled) return;
        setDocuments(data.documents);
        setTotal(data.total);
        setNextOffset(data.next_offset);
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Failed to load documents");
        setDocuments([]);
        setTotal(0);
        setNextOffset(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [applied]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setApplied({ ...draft });
  }

  async function onLoadMore() {
    if (nextOffset === null) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchDocuments(applied, nextOffset);
      setDocuments((current) => [...current, ...data.documents]);
      setTotal(data.total);
      setNextOffset(data.next_offset);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load documents");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>EPA final rules</h1>
      <p className="lede">
        Recent Environmental Protection Agency rules from the Federal Register.
      </p>

      <form className="filters" onSubmit={onSubmit}>
        <label>
          Search
          <input
            value={draft.q}
            onChange={(event) => setDraft({ ...draft, q: event.target.value })}
            placeholder="Title or abstract"
          />
        </label>
        <label>
          Published from
          <input
            type="date"
            value={draft.published_from}
            onChange={(event) =>
              setDraft({ ...draft, published_from: event.target.value })
            }
          />
        </label>
        <label>
          Published to
          <input
            type="date"
            value={draft.published_to}
            onChange={(event) =>
              setDraft({ ...draft, published_to: event.target.value })
            }
          />
        </label>
        <button type="submit" disabled={loading}>
          Apply
        </button>
      </form>

      <p className={`status${error ? " error" : ""}`}>
        {error
          ? error
          : loading && documents.length === 0
            ? "Loading…"
            : `${documents.length} of ${total} documents`}
      </p>

      {documents.length === 0 && !loading && !error ? (
        <p className="empty">No documents match.</p>
      ) : (
        <ul className="list">
          {documents.map((doc) => (
            <li className="card" key={doc.document_number}>
              <h2>
                {doc.html_url ? (
                  <a href={doc.html_url} target="_blank" rel="noreferrer">
                    {doc.title}
                  </a>
                ) : (
                  doc.title
                )}
              </h2>
              <div className="meta">
                <span>{doc.document_number}</span>
                <span>Published {doc.publication_date}</span>
                <span>Effective {doc.effective_on ?? "—"}</span>
                {doc.agency_names.length > 0 ? (
                  <span>{doc.agency_names.join(", ")}</span>
                ) : null}
              </div>
              {doc.abstract ? <p className="abstract">{doc.abstract}</p> : null}
            </li>
          ))}
        </ul>
      )}

      {nextOffset !== null ? (
        <button
          className="secondary"
          type="button"
          onClick={onLoadMore}
          disabled={loading}
        >
          {loading ? "Loading…" : "Load more"}
        </button>
      ) : null}
    </main>
  );
}

async function fetchDocuments(
  filters: Filters,
  offset: number
): Promise<DocumentsResponse> {
  const params = new URLSearchParams();
  if (filters.q.trim()) params.set("q", filters.q.trim());
  if (filters.published_from) params.set("published_from", filters.published_from);
  if (filters.published_to) params.set("published_to", filters.published_to);
  params.set("offset", String(offset));

  const response = await fetch(`/api/documents?${params.toString()}`);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || `Request failed (${response.status})`);
  }
  return payload as DocumentsResponse;
}
