import { NextRequest, NextResponse } from "next/server";
import { getPool } from "@/lib/db";

export const dynamic = "force-dynamic";

const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
const PAGE_SIZE = 20;

function escapeLike(value: string): string {
  return value.replace(/([\\%_])/g, "\\$1");
}

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl;
  const q = (searchParams.get("q") ?? "").trim();
  const publishedFrom = searchParams.get("published_from");
  const publishedTo = searchParams.get("published_to");
  const offsetRaw = searchParams.get("offset") ?? "0";

  if (publishedFrom && !DATE_RE.test(publishedFrom)) {
    return NextResponse.json(
      { error: "published_from must be YYYY-MM-DD" },
      { status: 400 }
    );
  }
  if (publishedTo && !DATE_RE.test(publishedTo)) {
    return NextResponse.json(
      { error: "published_to must be YYYY-MM-DD" },
      { status: 400 }
    );
  }

  const offset = Number(offsetRaw);
  if (!Number.isInteger(offset) || offset < 0) {
    return NextResponse.json(
      { error: "offset must be a non-negative integer" },
      { status: 400 }
    );
  }

  const qParam = q.length ? escapeLike(q) : null;
  const fromParam = publishedFrom || null;
  const toParam = publishedTo || null;

  const where = `
    WHERE ($1::date IS NULL OR publication_date >= $1)
      AND ($2::date IS NULL OR publication_date <= $2)
      AND (
        $3::text IS NULL
        OR title ILIKE '%' || $3 || '%' ESCAPE '\\'
        OR abstract ILIKE '%' || $3 || '%' ESCAPE '\\'
      )
  `;

  const pool = getPool();
  const client = await pool.connect();
  try {
    const countResult = await client.query(
      `SELECT COUNT(*)::int AS total FROM documents ${where}`,
      [fromParam, toParam, qParam]
    );
    const total = countResult.rows[0].total as number;
    const result = await client.query(
      `SELECT document_number, title,
              publication_date::text AS publication_date,
              effective_on::text AS effective_on,
              abstract, agency_names, html_url
       FROM documents
       ${where}
       ORDER BY publication_date DESC, document_number DESC
       LIMIT $4 OFFSET $5`,
      [fromParam, toParam, qParam, PAGE_SIZE, offset]
    );

    const nextOffset = offset + PAGE_SIZE < total ? offset + PAGE_SIZE : null;
    return NextResponse.json({
      documents: result.rows,
      offset,
      limit: PAGE_SIZE,
      total,
      next_offset: nextOffset,
    });
  } finally {
    client.release();
  }
}
