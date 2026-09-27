"""Postgres database module for regulatory documents ingestion"""

import os
from dataclasses import dataclass
from datetime import date
import psycopg
from data_cleaning import clean_text


@dataclass(frozen=True)
class DocumentRow:
    document_number: str
    title: str
    publication_date: date
    effective_on: date | None
    abstract: str | None
    agency_names: list[str]
    html_url: str
    raw_json: dict


def connect(database_url: str | None = None) -> psycopg.Connection:
    url = database_url or os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return psycopg.connect(url)


def parse_date(value) -> date | None:
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip()[:10])
    except ValueError:
        return None


def normalise_document(raw: dict) -> DocumentRow | None:
    """Clean a raw API document into a DocumentRow. Returns None if invalid."""
    number = (raw.get("document_number") or "").strip()
    pub_date = parse_date(raw.get("publication_date"))
    if not number or pub_date is None:
        return None

    agency_names = [
        a.get("name") or a.get("raw_name", "Unknown")
        for a in (raw.get("agencies") or [])
        if isinstance(a, dict)
    ]

    return DocumentRow(
        document_number=number,
        title=clean_text(raw.get("title")) or "Untitled",
        publication_date=pub_date,
        effective_on=parse_date(raw.get("effective_on")),
        abstract=clean_text(raw.get("abstract")),
        agency_names=agency_names,
        html_url=raw.get("html_url", ""),
        raw_json=raw,
    )


UPSERT_SQL = """
    INSERT INTO documents (
        document_number, title, abstract,
        publication_date, effective_on,
        agency_names, html_url, raw_json
    ) VALUES (
        %(document_number)s, %(title)s, %(abstract)s,
        %(publication_date)s, %(effective_on)s,
        %(agency_names)s, %(html_url)s, %(raw_json)s
    )
    ON CONFLICT (document_number) DO UPDATE SET
        title            = EXCLUDED.title,
        abstract         = EXCLUDED.abstract,
        publication_date = EXCLUDED.publication_date,
        effective_on     = EXCLUDED.effective_on,
        agency_names     = EXCLUDED.agency_names,
        html_url         = EXCLUDED.html_url,
        raw_json         = EXCLUDED.raw_json,
        ingested_at      = NOW()
"""


def upsert_documents(conn: psycopg.Connection, rows: list[DocumentRow]) -> int:
    """Upsert documents into Postgres. Returns count of rows affected."""
    with conn.cursor() as cur:
        for row in rows:
            cur.execute(UPSERT_SQL, {
                "document_number": row.document_number,
                "title": row.title,
                "abstract": row.abstract,
                "publication_date": row.publication_date,
                "effective_on": row.effective_on,
                "agency_names": row.agency_names,
                "html_url": row.html_url,
                "raw_json": psycopg.types.json.Json(row.raw_json),
            })
    conn.commit()
    return len(rows)
