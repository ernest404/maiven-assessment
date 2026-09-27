import os
from datetime import date
from pathlib import Path

import psycopg
import pytest
from dotenv import load_dotenv

from db import DocumentRow, normalise_document, upsert_documents


def _sample_raw(**overrides):
    raw = {
        "document_number": "TEST-0001",
        "title": "  Test <em>Rule</em> ",
        "abstract": "  Hello &amp; <em>world</em>  ",
        "publication_date": "2025-01-15",
        "effective_on": "2025-02-01",
        "agencies": [{"name": "Environmental Protection Agency"}],
        "html_url": "https://example.com/test",
    }
    raw.update(overrides)
    return raw


@pytest.fixture()
def conn():
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL not set")
    connection = psycopg.connect(url, autocommit=False)
    yield connection
    connection.rollback()
    connection.close()


# --- normalise_document ---

def test_normalise_cleans_text():
    row = normalise_document(_sample_raw())
    assert row is not None
    assert row.title == "Test Rule"
    assert row.abstract == "Hello & world"
    assert row.publication_date == date(2025, 1, 15)
    assert row.agency_names == ["Environmental Protection Agency"]


def test_normalise_rejects_missing_number():
    assert normalise_document(_sample_raw(document_number="")) is None


def test_normalise_rejects_bad_date():
    assert normalise_document(_sample_raw(publication_date="not-a-date")) is None


# --- upsert idempotency ---

def _make_row(doc_number="TEST-0001", title="Test Rule"):
    return DocumentRow(
        document_number=doc_number,
        title=title,
        publication_date=date(2025, 1, 15),
        effective_on=date(2025, 2, 1),
        abstract="test abstract",
        agency_names=["EPA"],
        html_url="https://example.com/test",
        raw_json={"document_number": doc_number},
    )


def test_upsert_no_duplicates(conn):
    row = _make_row()
    upsert_documents(conn, [row])
    upsert_documents(conn, [row])

    cur = conn.execute(
        "SELECT COUNT(*) FROM documents WHERE document_number = %s",
        ("TEST-0001",),
    )
    assert cur.fetchone()[0] == 1


def test_upsert_updates_fields(conn):
    upsert_documents(conn, [_make_row(title="Original")])
    upsert_documents(conn, [_make_row(title="Updated")])

    cur = conn.execute(
        "SELECT title FROM documents WHERE document_number = %s",
        ("TEST-0001",),
    )
    assert cur.fetchone()[0] == "Updated"
