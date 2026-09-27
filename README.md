# EPA rules tracker

A small ingest-and-search pipeline for recent Environmental Protection Agency
final rules from the [Federal Register API](https://www.federalregister.gov/developers/documentation/api/v1).
Python fetches and normalises documents into Postgres. A Next.js App Router
page lists them with date filters, text search, and pagination.