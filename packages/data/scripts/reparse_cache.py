"""Re-parse cached HTML without hitting the network.

Reads the HTML cache produced by a previous crawl
(``/data/raw/transparencia/html/*.html`` + ``*.json`` metadata) and re-runs the
parser on every page, regenerating ``pages.jsonl`` and the Parquet exports.

Use this to validate parser changes against the exact same input the previous
crawl downloaded — zero network requests, no load on the source server.
"""

import json
import logging
from pathlib import Path

from scrapers.transparencia.parse import TransparenciaParser
from scrapers.transparencia.storage import TransparenciaStorage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("reparse-cache")

CACHE_DIR = Path("/data/raw/transparencia/html")
RAW_DIR = Path("/data/raw/transparencia")
WAREHOUSE_DIR = Path("/data/warehouse")
BASE_URL = "https://transparencia.gob.es"


def main() -> None:
    parser = TransparenciaParser()
    jsonl_path = RAW_DIR / "pages.jsonl"
    if jsonl_path.exists():
        jsonl_path.unlink()
    storage = TransparenciaStorage(raw_dir=RAW_DIR, warehouse_dir=WAREHOUSE_DIR)

    metas = sorted(CACHE_DIR.glob("*.json"))
    logger.info("found %d cached pages", len(metas))

    parsed = 0
    for meta_path in metas:
        html_path = meta_path.with_suffix(".html")
        if not html_path.exists():
            logger.warning("missing html for %s", meta_path.name)
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        path = meta.get("url", "")
        url = path if path.startswith("http") else f"{BASE_URL}{path}"
        html = html_path.read_text(encoding="utf-8")
        page = parser.parse(url, html)
        storage.save_page(page)
        parsed += 1

    storage.flush()
    logger.info("reparsed %d pages -> %s", parsed, storage.page_count)


if __name__ == "__main__":
    main()
