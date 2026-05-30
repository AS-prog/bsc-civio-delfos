import hashlib
import json
import time
from pathlib import Path
from typing import Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

USER_AGENT = (
    "bsc-civio-delfos/0.1 (hackathon; +https://github.com/bsc-civio-delfos)"
)


class TransparenciaFetcher:
    BASE_URL = "https://transparencia.gob.es"

    def __init__(
        self,
        rate_limit: float = 1.0,
        cache_dir: Optional[Path] = None,
        user_agent: Optional[str] = None,
    ):
        self.rate_limit = rate_limit
        self.cache_dir = cache_dir
        self._last_request = 0.0
        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers={"User-Agent": user_agent or USER_AGENT},
            follow_redirects=True,
            timeout=30.0,
        )

    def _wait_rate_limit(self) -> None:
        elapsed = time.monotonic() - self._last_request
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)

    def _cache_path(self, path: str) -> Path:
        raw = path if path.startswith("/") else f"/{path}"
        h = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return self.cache_dir / f"{h}.html"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def fetch(self, path: str, use_cache: bool = True) -> Optional[str]:
        if self.cache_dir and use_cache:
            cache_path = self._cache_path(path)
            if cache_path.exists():
                cache_meta = cache_path.with_suffix(".json")
                if cache_meta.exists():
                    return cache_path.read_text(encoding="utf-8")

        self._wait_rate_limit()

        try:
            resp = self.client.get(path)
            self._last_request = time.monotonic()
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

        html = resp.text

        if self.cache_dir and use_cache and html:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            cache_path = self._cache_path(path)
            cache_path.write_text(html, encoding="utf-8")
            cache_path.with_suffix(".json").write_text(
                json.dumps({"url": path, "status": resp.status_code}),
                encoding="utf-8",
            )

        return html

    def close(self) -> None:
        self.client.close()
