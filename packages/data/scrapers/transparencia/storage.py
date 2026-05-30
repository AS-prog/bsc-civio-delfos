import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import polars as pl

from scrapers.transparencia.models import PageData

logger = logging.getLogger(__name__)


class TransparenciaStorage:

    def __init__(
        self,
        raw_dir: Path,
        warehouse_dir: Optional[Path] = None,
        jsonl_path: Optional[Path] = None,
    ):
        self.raw_dir = raw_dir
        self.warehouse_dir = warehouse_dir
        self._pages: list[PageData] = []
        self._jsonl_path = jsonl_path or raw_dir / "pages.jsonl"
        self._jsonl_path.parent.mkdir(parents=True, exist_ok=True)

    def save_page(self, page: PageData) -> None:
        page.crawled_at = datetime.now(timezone.utc).isoformat()
        self._pages.append(page)
        line = {
            "url": page.url,
            "canonical": page.canonical,
            "status_code": page.status_code,
            "breadcrumb": page.breadcrumb,
            "title": page.title,
            "updated_at": page.updated_at,
            "section_count": len(page.sections),
            "accordion_count": len(page.accordion_items),
            "external_link_count": len(page.external_links),
            "internal_link_count": len(page.internal_links),
            "crawled_at": page.crawled_at,
        }
        with self._jsonl_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")

    def save_pages_parquet(self) -> Path:
        if not self.warehouse_dir:
            self.warehouse_dir = self.raw_dir / "warehouse"
        self.warehouse_dir.mkdir(parents=True, exist_ok=True)

        rows = []
        for p in self._pages:
            rows.append(
                {
                    "url": p.url,
                    "canonical": p.canonical or "",
                    "status_code": p.status_code or 0,
                    "breadcrumb": " > ".join(p.breadcrumb),
                    "title": p.title or "",
                    "updated_at": p.updated_at or "",
                    "section_count": len(p.sections),
                    "accordion_count": len(p.accordion_items),
                    "external_links": len(p.external_links),
                    "internal_links": len(p.internal_links),
                    "crawled_at": p.crawled_at or "",
                }
            )

        if not rows:
            raise ValueError("no pages to export")

        path = self.warehouse_dir / "transparencia_pages.parquet"
        df = pl.DataFrame(rows)
        df.write_parquet(str(path))
        logger.info("exported %d rows to %s", len(rows), path)
        return path

    def save_page_detail_parquet(self) -> Optional[Path]:
        sections_rows = []
        accordion_rows = []
        links_rows = []

        for p in self._pages:
            for s in p.sections:
                sections_rows.append(
                    {
                        "url": p.url,
                        "heading": s.heading,
                        "text": s.text,
                    }
                )
            for ord_, item in enumerate(p.accordion_items, start=1):
                accordion_rows.append(
                    {
                        "url": p.url,
                        "ord": ord_,
                        "title": item.title,
                        "content": item.content,
                    }
                )
            for l in p.external_links:
                links_rows.append(
                    {
                        "url": p.url,
                        "target_url": l.url,
                        "text": l.text,
                    }
                )

        if not self.warehouse_dir:
            return None

        if sections_rows:
            path = self.warehouse_dir / "transparencia_sections.parquet"
            pl.DataFrame(sections_rows).write_parquet(str(path))
            logger.info("exported %d sections to %s", len(sections_rows), path)

        if accordion_rows:
            path = self.warehouse_dir / "transparencia_accordion.parquet"
            pl.DataFrame(accordion_rows).write_parquet(str(path))
            logger.info(
                "exported %d accordion items to %s",
                len(accordion_rows),
                path,
            )

        if links_rows:
            path = self.warehouse_dir / "transparencia_links.parquet"
            pl.DataFrame(links_rows).write_parquet(str(path))
            logger.info("exported %d links to %s", len(links_rows), path)

        return self.warehouse_dir / "transparencia_pages.parquet"

    def flush(self) -> None:
        if self._pages and self.warehouse_dir:
            self.save_pages_parquet()
            self.save_page_detail_parquet()

    @property
    def page_count(self) -> int:
        return len(self._pages)
