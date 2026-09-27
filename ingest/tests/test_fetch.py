from fetch import fetch_documents
from unittest.mock import patch, MagicMock


def _mock_responses():
    """Simulate two pages with a duplicate document."""
    page1 = MagicMock()
    page1.json.return_value = {
        "results": [
            {"document_number": "A", "title": "One"},
            {"document_number": "B", "title": "Two"},
        ],
        "next_page_url": "https://example.com/page2",
    }
    page1.raise_for_status = MagicMock()

    page2 = MagicMock()
    page2.json.return_value = {
        "results": [
            {"document_number": "B", "title": "Dup"},
            {"document_number": "C", "title": "Three"},
        ],
        "next_page_url": None,
    }
    page2.raise_for_status = MagicMock()

    return [page1, page2]


@patch("fetch.requests.get")
def test_follows_pagination_and_deduplicates(mock_get):
    mock_get.side_effect = _mock_responses()
    docs = fetch_documents(limit=3, per_page=2)
    assert [d["document_number"] for d in docs] == ["A", "B", "C"]
