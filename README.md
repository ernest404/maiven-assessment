# EPA rules tracker

A small ingest-and-search pipeline for recent Environmental Protection Agency
final rules from the [Federal Register API](https://www.federalregister.gov/developers/documentation/api/v1).
Python fetches and normalises documents into Postgres. A Next.js App Router
page lists them with date filters, text search, and pagination.

## Requirements

- Docker
- Python 3.11+
- Node 20+

## Quick Start

### 1. Start the database

```bash
cd db
docker-compose up -d
```

This starts Postgres on port **5433** and applies the schema from `db.sql` automatically.

The default connection string is:

```
DATABASE_URL=postgresql://maiven:maiven@localhost:5433/regulations
```

### 2. Ingest documents

```bash
cd ingest
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python ingest.py
```

Fetches 100 EPA rules and upserts them into Postgres. Re-running is safe — no duplicates.

### 3. Start the web app

```bash
cd web-app
npm install
npm run dev
```

Open http://localhost:3000.

### 4. Run tests

```bash
cd ingest
source venv/bin/activate
pytest -v
```

## Project structure

```
├── .env                            # DATABASE_URL
├── db/
│   ├── docker-compose.yml          # Postgres container
│   └── db.sql                      # Table schema + index
├── ingest/
│   ├── ingest.py                   # Entry point — fetch, clean, store
│   ├── fetch.py                    # Federal Register API client
│   ├── database.py                 # Postgres connection, document model, upsert
│   ├── data_cleaning.py            # Text normalisation (HTML strip, whitespace)
│   ├── requirements.txt
│   └── tests/
│       ├── test_clean.py           # HTML stripping, whitespace, edge cases
│       ├── test_db.py              # Normalisation + upsert idempotency
│       └── test_fetch.py           # Pagination + deduplication (mocked)
└── web-app/
    ├── app/
    │   ├── page.tsx                # Document listing with search/filter/pagination
    │   ├── layout.tsx              # Root layout
    │   └── api/documents/
    │       └── route.ts            # GET /api/documents
    └── lib/
        ├── db.ts                   # Postgres pool
        └── types.ts                # Shared TypeScript types
```

## API

**`GET /api/documents`**

| Param  | Type   | Description                               |
|--------|--------|-------------------------------------------|
| `page` | number | Page number (default 1, 20 per page)      |
| `from` | date   | Min publication date (YYYY-MM-DD)         |
| `to`   | date   | Max publication date (YYYY-MM-DD)         |
| `q`    | string | Case-insensitive search on title/abstract |

Returns `{ documents, page, hasMore }`.

## What I'd do differently with more time

**Ingest** — Run the ingest on a schedule (e.g. cron-job) so new rules appear automatically.
Persist ingest_runs (cursor, counts, errors). Fetch only what is newer than the last successful watermark. Add retries with exponential backoff for API failures and use `httpx` with async for faster fetching across different pages.

**Database** —  Keep current state on documents, and a document_versions table on (document_number, content_hash) so corrections are visible. Add connection pooling (PgBouncer) for the web app under load. Replace `ILIKE` with Postgres full-text search (`tsvector`/`tsquery`) for faster, ranked results as the dataset grows

**API** — Add rate limiting, request validation, and proper error responses with consistent error codes. Paginate with cursor-based pagination instead of offset for stable results. 

**Frontend** — Add loading skeletons, error states with retry, and URL-synced filters so searches are shareable. Add end-to-end tests.

**Infrastructure** — Containerise the ingest and web app (Dockerfiles), add a single `docker-compose.yml` at the root to run the full stack, set up CI with GitHub Actions for linting and tests, and manage secrets through environment variables in the deployment platform.
