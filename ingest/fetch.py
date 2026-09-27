"""Federal Register API client."""

from urllib.parse import urlencode
import requests

BASE_URL = "https://www.federalregister.gov/api/v1/documents.json"
FIELDS = [
    "title",
    "document_number",
    "publication_date",
    "effective_on",
    "abstract",
    "agencies",
    "html_url",
]


def build_url(per_page: int = 20) -> str:
    params: list[tuple[str, str]] = [
        ("conditions[type][]", "RULE"),
        ("conditions[agencies][]", "environmental-protection-agency"),
        ("per_page", str(per_page)),
    ]
    for field in FIELDS:
        params.append(("fields[]", field))
    return f"{BASE_URL}?{urlencode(params)}"


def fetch_documents(limit: int = 100, per_page: int = 20) -> list[dict]:
    """Fetch EPA rules, following next_page_url until `limit` unique docs."""
    collected: dict[str, dict] = {}
    url: str | None = build_url(per_page)
    page = 0

    while url and len(collected) < limit:
        page += 1
        print(f"Fetching page {page}… ({len(collected)} documents so far)")

        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results") or []
        if not results:
            break

        for doc in results:
            number = (doc.get("document_number") or "").strip()
            if not number or number in collected:
                continue
            collected[number] = doc
            if len(collected) >= limit:
                break

        url = data.get("next_page_url")

    print(f"Fetched {len(collected)} documents total.")
    return list(collected.values())
