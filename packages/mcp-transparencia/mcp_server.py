from __future__ import annotations

import os
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import psycopg
from mcp.server.fastmcp import FastMCP
from psycopg.rows import dict_row

mcp = FastMCP("transparencia")

READ_ONLY_PREFIXES = ("select", "with", "explain")


def _env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name) or default


def _connect() -> psycopg.Connection[Any]:
    return psycopg.connect(
        host=_env("POSTGRES_HOST", "localhost"),
        port=int(_env("POSTGRES_PORT", "5432") or "5432"),
        dbname=_env("POSTGRES_DB", "civio"),
        user=_env("POSTGRES_USER", "civio"),
        password=_env("POSTGRES_PASSWORD", "change-me-locally"),
        row_factory=dict_row,
    )


def _json(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, list):
        return [_json(item) for item in value]
    if isinstance(value, dict):
        return {key: _json(item) for key, item in value.items()}
    return value


def _rows(query: str, params: tuple[Any, ...] = (), limit: int = 100) -> list[dict[str, Any]]:
    with _connect() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("SET TRANSACTION READ ONLY")
                cur.execute(query, params)
                return [_json(row) for row in cur.fetchmany(limit)]


def _one(query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    rows = _rows(query, params, limit=1)
    return rows[0] if rows else None


def _is_read_only_sql(query: str) -> bool:
    normalized = query.strip().lower()
    if not normalized:
        return False
    normalized = re.sub(r"^/\*.*?\*/", "", normalized, flags=re.DOTALL).strip()
    if not normalized.startswith(READ_ONLY_PREFIXES):
        return False
    without_trailing_semicolon = normalized[:-1] if normalized.endswith(";") else normalized
    return ";" not in without_trailing_semicolon


@mcp.tool()
def execute_sql(query: str, limit: int = 100) -> dict[str, Any]:
    """Execute one read-only SQL query against the Transparencia Postgres database.

    Only SELECT, WITH, and EXPLAIN statements are accepted. Results are capped by
    `limit` to keep MCP responses small. The transaction is forced read-only.
    """
    if limit < 1 or limit > 500:
        raise ValueError("limit must be between 1 and 500")
    if not _is_read_only_sql(query):
        raise ValueError("Only one read-only SELECT/WITH/EXPLAIN statement is allowed")
    rows = _rows(query, limit=limit)
    return {"rows": rows, "returned": len(rows), "limit": limit}


@mcp.tool()
def get_page(url: str) -> dict[str, Any]:
    """Return one Transparencia page with sections, accordion items, and classified links."""
    page = _one(
        """
        SELECT url, canonical, status_code, breadcrumb, title, updated_at,
               section_count, accordion_count, external_link_count,
               internal_link_count, crawled_at, materia_slug, materia_label
        FROM transparencia.pages
        WHERE url = %s
        """,
        (url,),
    )
    if page is None:
        return {"page": None, "sections": [], "accordion": [], "links": []}
    sections = _rows(
        """
        SELECT ord, heading, text, content
        FROM transparencia.sections
        WHERE page_url = %s
        ORDER BY ord
        """,
        (url,),
        limit=500,
    )
    accordion = _rows(
        """
        SELECT ord, title, content
        FROM transparencia.accordion
        WHERE page_url = %s
        ORDER BY ord
        """,
        (url,),
        limit=500,
    )
    links = _rows(
        """
        SELECT ord, target_url, target_host, anchor_text, code, label, category
        FROM transparencia.v_link_categories
        WHERE source_page_url = %s
          AND NOT is_noise
        ORDER BY ord
        """,
        (url,),
        limit=500,
    )
    return {"page": page, "sections": sections, "accordion": accordion, "links": links}


@mcp.tool()
def search_pages(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Search pages by Spanish full-text search over titles, sections, and page metadata."""
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")
    return _rows(
        """
        SELECT url, title, materia_slug, materia_label,
               ts_rank(search_tsv, plainto_tsquery('spanish', %s)) AS rank
        FROM transparencia.v_search_pages
        WHERE search_tsv @@ plainto_tsquery('spanish', %s)
        ORDER BY rank DESC, title NULLS LAST
        LIMIT %s
        """,
        (query, query, limit),
        limit=limit,
    )


@mcp.tool()
def list_organisms() -> list[dict[str, Any]]:
    """Return summary rows by materia.

    Historical name kept for compatibility: these rows are thematic materias,
    not issuing organizations.
    """
    return _rows(
        """
        SELECT materia_slug, materia_label, page_count, link_count,
               download_count, boe_count, pap_hacienda_count, subvenciones_count
        FROM transparencia.v_organisms
        ORDER BY page_count DESC, materia_slug
        """,
        limit=100,
    )


@mcp.tool()
def get_external_links(domain: str, limit: int = 100) -> list[dict[str, Any]]:
    """Return classified outgoing links whose host contains `domain`."""
    if limit < 1 or limit > 500:
        raise ValueError("limit must be between 1 and 500")
    return _rows(
        """
        SELECT source_page_url, ord, target_url, target_host, anchor_text,
               code, label, category, materia_slug, materia_label
        FROM transparencia.v_link_categories
        WHERE target_host ILIKE %s
          AND scope <> 'internal'
          AND NOT is_noise
        ORDER BY source_page_url, ord
        LIMIT %s
        """,
        (f"%{domain}%", limit),
        limit=limit,
    )


@mcp.tool()
def get_links_by_category(
    category: str,
    materia_slug: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Return links by curated category, optionally scoped to one materia slug."""
    if limit < 1 or limit > 500:
        raise ValueError("limit must be between 1 and 500")
    if materia_slug:
        return _rows(
            """
            SELECT source_page_url, ord, target_url, target_host, anchor_text,
                   code, label, category, materia_slug, materia_label
            FROM transparencia.v_link_categories
            WHERE category = %s
              AND materia_slug = %s
            ORDER BY source_page_url, ord
            LIMIT %s
            """,
            (category, materia_slug, limit),
            limit=limit,
        )
    return _rows(
        """
        SELECT source_page_url, ord, target_url, target_host, anchor_text,
               code, label, category, materia_slug, materia_label
        FROM transparencia.v_link_categories
        WHERE category = %s
        ORDER BY source_page_url, ord
        LIMIT %s
        """,
        (category, limit),
        limit=limit,
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
