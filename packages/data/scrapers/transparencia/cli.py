import logging
import sys
from pathlib import Path

import typer

from scrapers.transparencia.crawl import TransparenciaCrawler
from scrapers.transparencia.fetch import TransparenciaFetcher
from scrapers.transparencia.parse import TransparenciaParser
from scrapers.transparencia.storage import TransparenciaStorage

app = typer.Typer(
    name="transparencia",
    help="Scraper del Portal de Transparencia (publicidad-activa)",
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger("transparencia-cli")

RAW_DIR = Path("/data/raw/transparencia")
WAREHOUSE_DIR = Path("/data/warehouse")


def _build_crawler(
    rate_limit: float = 1.0,
    no_cache: bool = False,
):
    fetcher = TransparenciaFetcher(
        rate_limit=rate_limit,
        cache_dir=None if no_cache else RAW_DIR / "html",
    )
    parser = TransparenciaParser()
    storage = TransparenciaStorage(
        raw_dir=RAW_DIR,
        warehouse_dir=WAREHOUSE_DIR,
    )
    return TransparenciaCrawler(fetcher=fetcher, parser=parser, storage=storage)


@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Debug log"),
):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@app.command()
def discover(
    rate_limit: float = typer.Option(
        1.0, "--rate-limit", "-r", help="Seconds between requests"
    ),
    no_cache: bool = typer.Option(
        False, "--no-cache", help="Skip HTML cache"
    ),
):
    crawler = _build_crawler(rate_limit=rate_limit, no_cache=no_cache)
    try:
        urls = crawler.discover()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        url_path = RAW_DIR / "urls.csv"
        with url_path.open("w", encoding="utf-8") as f:
            f.write("path\n")
            for u in sorted(urls):
                f.write(f"{u}\n")
        logger.info("discovered %d URLs -> %s", len(urls), url_path)
    finally:
        crawler.fetcher.close()


@app.command()
def crawl(
    limit: int = typer.Option(None, "--limit", "-l", help="Max pages to crawl"),
    rate_limit: float = typer.Option(
        1.0, "--rate-limit", "-r", help="Seconds between requests"
    ),
    no_cache: bool = typer.Option(
        False, "--no-cache", help="Skip HTML cache"
    ),
):
    crawler = _build_crawler(rate_limit=rate_limit, no_cache=no_cache)
    try:
        seeds = [
            "/publicidad-activa/por-materias",
            "/publicidad-activa/por-materias/organizacion-empleo",
        ]
        urls = crawler.discover(seeds=seeds)
        pages = crawler.crawl(urls=urls, limit=limit)
        logger.info(
            "crawl finished: %d pages, %d unique URLs discovered",
            len(pages),
            len(urls),
        )
    finally:
        crawler.fetcher.close()


@app.command()
def export(
    format: str = typer.Option(
        "parquet", "--format", "-f", help="Output format (parquet, csv)"
    ),
):
    warehouse = WAREHOUSE_DIR
    if not warehouse.exists():
        logger.error("warehouse dir %s does not exist; run crawl first")
        raise typer.Exit(code=1)

    parquet_path = warehouse / "transparencia_pages.parquet"
    if not parquet_path.exists():
        logger.error("no parquet data found at %s", parquet_path)
        raise typer.Exit(code=1)

    if format == "csv":
        import polars as pl

        df = pl.read_parquet(str(parquet_path))
        csv_path = warehouse / "transparencia_pages.csv"
        df.write_csv(str(csv_path))
        logger.info("exported CSV -> %s", csv_path)
    else:
        logger.info("parquet already at %s", parquet_path)


if __name__ == "__main__":
    app()
