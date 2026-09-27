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
