import logging
from collections import deque
from typing import Optional

from scrapers.transparencia.fetch import TransparenciaFetcher
from scrapers.transparencia.models import PageData
from scrapers.transparencia.parse import TransparenciaParser
from scrapers.transparencia.storage import TransparenciaStorage

logger = logging.getLogger(__name__)

SEEDS = [
    "/publicidad-activa",
    "/publicidad-activa/por-materias",
]

EXCLUDED_PREFIXES = (
    "/ca/",
    "/eu/",
    "/gl/",
    "/va/",
    "/en/",
    "/content/dam/",
    "/etc.clientlibs/",
)


class TransparenciaCrawler:

    def __init__(
        self,
        fetcher: TransparenciaFetcher,
        parser: TransparenciaParser,
        storage: TransparenciaStorage,
    ):
        self.fetcher = fetcher
        self.parser = parser
        self.storage = storage

    def discover(self, seeds: Optional[list[str]] = None) -> set[str]:
        queue = deque(seeds or SEEDS)
        discovered: set[str] = set(seeds or SEEDS)
        logger.info("starting discovery with %d seeds", len(queue))

        while queue:
            path = queue.popleft()
            logger.debug("discovering %s", path)
            html = self.fetcher.fetch(path, use_cache=True)
            if html is None:
                continue
            links = self.parser.extract_links(html)
            for link in links:
                if link not in discovered and not link.startswith(
                    EXCLUDED_PREFIXES
                ):
                    discovered.add(link)
                    queue.append(link)

        logger.info("discovery complete: %d URLs found", len(discovered))
        return discovered

    def crawl(
        self,
        urls: set[str],
        limit: Optional[int] = None,
    ) -> list[PageData]:
        pages: list[PageData] = []
        urls_iter = sorted(urls)
        if limit:
            urls_iter = urls_iter[:limit]

        logger.info("crawling %d pages", len(urls_iter))
        for i, path in enumerate(urls_iter):
            logger.info("[%d/%d] %s", i + 1, len(urls_iter), path)
            html = self.fetcher.fetch(path, use_cache=True)
            if html is None:
                continue
            page = self.parser.parse(f"https://transparencia.gob.es{path}", html)
            pages.append(page)
            self.storage.save_page(page)

        self.storage.flush()
        logger.info("crawl complete: %d pages saved", len(pages))
        return pages
