CREATE TABLE IF NOT EXISTS documents (
  document_number  TEXT PRIMARY KEY,
  title            TEXT NOT NULL,
  abstract         TEXT NOT NULL DEFAULT '',
  publication_date DATE NOT NULL,
  effective_on     DATE,
  agency_names     TEXT[] NOT NULL DEFAULT '{}',
  html_url         TEXT,
  raw_json         JSONB NOT NULL,
  ingested_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS documents_publication_date_idx
  ON documents (publication_date DESC, document_number DESC);