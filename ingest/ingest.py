"""Fetch EPA final rules from the Federal Register and upsert into Postgres.

Usage:
    python ingest.py
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
from fetch import fetch_documents
from database import connect, normalise_document, upsert_documents

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def main() -> int:
    raw_docs = fetch_documents(limit=100, per_page=20)
    conn = connect()
    rows = []
    for raw in raw_docs:
        row = normalise_document(raw)
        if row is None:
            print(f"Skipping invalid document: {raw.get('document_number')!r}", file=sys.stderr)
            continue
        rows.append(row)

    with conn:
        count = upsert_documents(conn, rows)

    print(f"Upserted {count} documents.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
