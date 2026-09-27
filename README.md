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

### 1. Set Up the Database

#### Use Docker (no local Postgres needed)

```bash
cd db
docker-compose up -d
```

This starts Postgres on port **5433** (to avoid conflicts with a local instance) and runs `db.sql` automatically.

Then update the connection string in `.env` and `web/.env.local` if the defaults don't match your setup:

```
DATABASE_URL=postgresql://maiven:maiven@localhost:5433/regulations
```
