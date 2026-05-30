"""Load the Transparencia Parquet corpus into PostgreSQL.

The default warehouse lives outside this repository by design; do not copy the
Parquet files into git.
"""

from __future__ import annotations

import os
import re
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import polars as pl
import psycopg
import typer

app = typer.Typer(no_args_is_help=True)

ROOT_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_WAREHOUSE_DIR = PROJECT_ROOT / "data" / "warehouse"
SCHEMA_SQL = ROOT_DIR / "sql" / "schema.sql"
DOWNLOAD_EXTENSIONS = {"pdf", "xls", "xlsx", "csv", "ods"}
TRANSPARENCIA_HOST = "transparencia.gob.es"


def _env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name) or default


def _connect() -> psycopg.Connection[Any]:
    return psycopg.connect(
        host=_env("POSTGRES_HOST", "localhost"),
        port=int(_env("POSTGRES_PORT", "5432") or "5432"),
        dbname=_env("POSTGRES_DB", "civio"),
        user=_env("POSTGRES_USER", "civio"),
        password=_env("POSTGRES_PASSWORD", "change-me-locally"),
    )


def _read_parquet(path: Path) -> pl.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required Parquet file not found: {path}")
    return pl.read_parquet(path)


def _clean(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and value != value:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def _text(value: Any) -> str | None:
    value = _clean(value)
    if value is None:
        return None
    if isinstance(value, list):
        return " > ".join(str(item).strip() for item in value if str(item).strip())
    return str(value)


def _int(value: Any) -> int:
    value = _clean(value)
    if value is None:
        return 0
    return int(value)


def _date(value: Any) -> date | None:
    value = _clean(value)
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    text = str(value)
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text[:10], fmt).date()
        except ValueError:
            pass
    return None


def _timestamp(value: Any) -> datetime | None:
    value = _clean(value)
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _breadcrumb(value: Any) -> list[str]:
    value = _clean(value)
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value)
    if " > " in text:
        return [part.strip() for part in text.split(" > ") if part.strip()]
    return [text]


def _slugify(value: str | None) -> str | None:
    if not value:
        return None
    slug = value.strip().lower()
    slug = re.sub(r"[^a-z0-9áéíóúüñ]+", "-", slug)
    slug = slug.strip("-")
    return slug or None


def _label_from_slug(value: str | None) -> str | None:
    if not value:
        return None
    return " ".join(part.capitalize() for part in value.split("-") if part)


def _materia_from_url(url: str | None) -> str | None:
    if not url:
        return None
    path = urlparse(url).path.strip("/")
    parts = path.split("/")
    if len(parts) >= 3 and parts[0] == "publicidad-activa" and parts[1] == "por-materias":
        return parts[2] or None
    if len(parts) >= 2 and parts[0] == "publicidad-activa":
        return parts[1] or None
    return None


def _materia(row: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    raw = _text(row.get("materias"))
    slug = _materia_from_url(_text(row.get("url"))) or _slugify(raw)
    label = raw or _label_from_slug(slug)
    return raw, slug, label


def _normalise_url(source_url: str, target_url: str | None) -> str | None:
    if not target_url:
        return None
    return urljoin(source_url, target_url.strip())


def _link_parts(source_url: str, target_url: str | None) -> dict[str, Any]:
    resolved = _normalise_url(source_url, target_url)
    if not resolved:
        return {
            "target_url": None,
            "target_host": None,
            "target_path": None,
            "file_extension": None,
            "is_download": False,
            "is_noise": True,
            "scope": "noise",
        }

    parsed = urlparse(resolved)
    host = parsed.netloc.lower() or None
    path = parsed.path or resolved
    extension = None
    match = re.search(r"\.([A-Za-z0-9]+)(?:$|[?#])", parsed.path)
    if match:
        extension = match.group(1).lower()

    is_noise = resolved.startswith("javascript:") or resolved.startswith("#")
    is_download = "/content/dam/" in parsed.path or extension in DOWNLOAD_EXTENSIONS
    is_internal = host == TRANSPARENCIA_HOST and parsed.path.startswith("/publicidad-activa/")

    if is_noise:
        scope = "noise"
    elif is_download:
        scope = "download"
    elif is_internal:
        scope = "internal"
    else:
        scope = "external"

    return {
        "target_url": resolved,
        "target_host": host,
        "target_path": path,
        "file_extension": extension,
        "is_download": is_download,
        "is_noise": is_noise,
        "scope": scope,
    }


def _copy_rows(
    conn: psycopg.Connection[Any],
    table: str,
    columns: list[str],
    rows: list[tuple[Any, ...]],
) -> None:
    if not rows:
        return
    column_sql = ", ".join(columns)
    with conn.cursor() as cur:
        with cur.copy(f"COPY {table} ({column_sql}) FROM STDIN") as copy:
            for row in rows:
                copy.write_row(row)


def _load_pages(conn: psycopg.Connection[Any], df: pl.DataFrame) -> int:
    rows: list[tuple[Any, ...]] = []
    for row in df.iter_rows(named=True):
        materia_raw, materia_slug, materia_label = _materia(row)
        rows.append(
            (
                _text(row.get("url")),
                _text(row.get("canonical")),
                _int(row.get("status_code")),
                _breadcrumb(row.get("breadcrumb")),
                _text(row.get("title")),
                _date(row.get("updated_at")),
                _int(row.get("section_count")),
                _int(row.get("accordion_count")),
                _int(row.get("external_links")),
                _int(row.get("internal_links")),
                _timestamp(row.get("crawled_at")),
                materia_raw,
                materia_slug,
                materia_label,
            )
        )
    _copy_rows(
        conn,
        "transparencia.pages",
        [
            "url",
            "canonical",
            "status_code",
            "breadcrumb",
            "title",
            "updated_at",
            "section_count",
            "accordion_count",
            "external_link_count",
            "internal_link_count",
            "crawled_at",
            "materia_raw",
            "materia_slug",
            "materia_label",
        ],
        rows,
    )
    return len(rows)


def _load_sections(conn: psycopg.Connection[Any], df: pl.DataFrame) -> int:
    rows: list[tuple[Any, ...]] = []
    ord_by_url: defaultdict[str, int] = defaultdict(int)
    for row in df.iter_rows(named=True):
        page_url = _text(row.get("url"))
        if not page_url:
            continue
        ord_by_url[page_url] += 1
        rows.append(
            (
                page_url,
                ord_by_url[page_url],
                _text(row.get("heading")),
                _text(row.get("text")),
                _text(row.get("content")),
                _text(row.get("materias")),
            )
        )
    _copy_rows(
        conn,
        "transparencia.sections",
        ["page_url", "ord", "heading", "text", "content", "materia_raw"],
        rows,
    )
    return len(rows)


def _load_accordion(conn: psycopg.Connection[Any], df: pl.DataFrame) -> int:
    rows: list[tuple[Any, ...]] = []
    for row in df.iter_rows(named=True):
        page_url = _text(row.get("url"))
        if not page_url:
            continue
        rows.append(
            (
                page_url,
                _int(row.get("ord")),
                _text(row.get("title")),
                _text(row.get("content")),
            )
        )
    _copy_rows(
        conn,
        "transparencia.accordion",
        ["page_url", "ord", "title", "content"],
        rows,
    )
    return len(rows)


def _load_links(conn: psycopg.Connection[Any], df: pl.DataFrame) -> int:
    rows: list[tuple[Any, ...]] = []
    ord_by_url: defaultdict[str, int] = defaultdict(int)
    for row in df.iter_rows(named=True):
        page_url = _text(row.get("url"))
        if not page_url:
            continue
        ord_by_url[page_url] += 1
        parts = _link_parts(page_url, _text(row.get("target_url")))
        if not parts["target_url"]:
            continue
        rows.append(
            (
                page_url,
                ord_by_url[page_url],
                parts["target_url"],
                parts["target_host"],
                parts["target_path"],
                _text(row.get("text")),
                parts["file_extension"],
                parts["scope"],
                parts["is_download"],
                parts["is_noise"],
                _text(row.get("materias")),
            )
        )
    _copy_rows(
        conn,
        "transparencia.links",
        [
            "source_page_url",
            "ord",
            "target_url",
            "target_host",
            "target_path",
            "anchor_text",
            "file_extension",
            "scope",
            "is_download",
            "is_noise",
            "materia_raw",
        ],
        rows,
    )
    return len(rows)


def _post_load(conn: psycopg.Connection[Any]) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            WITH picked AS (
                SELECT
                    l.id AS link_id,
                    lp.id AS pattern_id,
                    rt.id AS resource_type_id
                FROM transparencia.links l
                JOIN LATERAL (
                    SELECT lp.id, lp.resource_type_code
                    FROM transparencia.link_patterns lp
                    WHERE lp.enabled
                      AND (lp.host_match IS NULL OR COALESCE(l.target_host, '') ~* lp.host_match)
                      AND (
                          lp.path_regex IS NULL
                          OR COALESCE(l.target_path, '') ~* lp.path_regex
                          OR l.target_url ~* lp.path_regex
                      )
                    ORDER BY lp.priority DESC, lp.id ASC
                    LIMIT 1
                ) lp ON true
                JOIN transparencia.resource_types rt ON rt.code = lp.resource_type_code
            )
            UPDATE transparencia.links l
            SET pattern_id = picked.pattern_id,
                resource_type_id = picked.resource_type_id
            FROM picked
            WHERE picked.link_id = l.id;
            """
        )
        cur.execute(
            """
            UPDATE transparencia.pages p
            SET search_tsv = to_tsvector(
                'spanish',
                concat_ws(
                    ' ',
                    p.title,
                    array_to_string(p.breadcrumb, ' '),
                    p.materia_raw,
                    (
                        SELECT string_agg(concat_ws(' ', s.heading, s.text, s.content), ' ')
                        FROM transparencia.sections s
                        WHERE s.page_url = p.url
                    ),
                    (
                        SELECT string_agg(concat_ws(' ', a.title, a.content), ' ')
                        FROM transparencia.accordion a
                        WHERE a.page_url = p.url
                    )
                )
            );
            """
        )


def _verify(conn: psycopg.Connection[Any]) -> None:
    queries = [
        ("pages", "SELECT count(*) FROM transparencia.pages"),
        ("sections", "SELECT count(*) FROM transparencia.sections"),
        ("accordion", "SELECT count(*) FROM transparencia.accordion"),
        ("links", "SELECT count(*) FROM transparencia.links"),
    ]
    with conn.cursor() as cur:
        for label, query in queries:
            cur.execute(query)
            typer.echo(f"{label}: {cur.fetchone()[0]}")

        typer.echo("\nresource types:")
        cur.execute(
            """
            SELECT code, count(*)
            FROM transparencia.v_link_categories
            GROUP BY code
            ORDER BY count(*) DESC, code
            """
        )
        for code, count in cur.fetchall():
            typer.echo(f"  {code}: {count}")

        typer.echo("\nmaterias:")
        cur.execute(
            """
            SELECT materia_slug, materia_label, page_count, link_count
            FROM transparencia.v_organisms
            ORDER BY page_count DESC, materia_slug
            """
        )
        for slug, label, page_count, link_count in cur.fetchall():
            typer.echo(f"  {slug or '(sin-materia)'} | {label or ''}: {page_count} pages, {link_count} links")

        typer.echo("\nsearch sample: empleo")
        cur.execute(
            """
            SELECT title, url
            FROM transparencia.v_search_pages
            WHERE search_tsv @@ plainto_tsquery('spanish', 'empleo')
            LIMIT 5
            """
        )
        for title, url in cur.fetchall():
            typer.echo(f"  {title or '(sin titulo)'} -> {url}")


@app.command()
def main(
    warehouse_dir: Path = typer.Option(
        DEFAULT_WAREHOUSE_DIR,
        help="Directory containing transparencia_*.parquet files.",
    ),
    reset_schema: bool = typer.Option(
        False,
        help="Drop and recreate the transparencia schema before loading.",
    ),
    verify: bool = typer.Option(False, help="Print counts and classification checks."),
) -> None:
    pages_path = warehouse_dir / "transparencia_pages.parquet"
    sections_path = warehouse_dir / "transparencia_sections.parquet"
    accordion_path = warehouse_dir / "transparencia_accordion.parquet"
    links_path = warehouse_dir / "transparencia_links.parquet"

    pages = _read_parquet(pages_path)
    sections = _read_parquet(sections_path)
    accordion = _read_parquet(accordion_path)
    links = _read_parquet(links_path)

    schema_sql = SCHEMA_SQL.read_text(encoding="utf-8")

    with _connect() as conn:
        with conn.cursor() as cur:
            if reset_schema:
                cur.execute("DROP SCHEMA IF EXISTS transparencia CASCADE")
            cur.execute(schema_sql)
            cur.execute(
                """
                TRUNCATE
                    transparencia.links,
                    transparencia.accordion,
                    transparencia.sections,
                    transparencia.pages
                RESTART IDENTITY CASCADE
                """
            )

        page_count = _load_pages(conn, pages)
        section_count = _load_sections(conn, sections)
        accordion_count = _load_accordion(conn, accordion)
        link_count = _load_links(conn, links)
        _post_load(conn)

        typer.echo(
            f"loaded {page_count} pages, {section_count} sections, "
            f"{accordion_count} accordion items, {link_count} links "
            f"from {warehouse_dir}"
        )
        if verify:
            _verify(conn)


if __name__ == "__main__":
    app()
