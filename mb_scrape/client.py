"""HTTP client with session management, retries, and rate limiting."""

import time
import logging
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from mb_scrape.constants import DEFAULT_HEADERS

logger = logging.getLogger(__name__)


class MagicBricksClient:
    """HTTP client specialized for querying MagicBricks with polite rate limiting and retry handling."""

    def __init__(
        self,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 20,
        delay: float = 1.0,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        proxies: Optional[Dict[str, str]] = None,
    ):
        self.timeout = timeout
        self.delay = delay
        self.proxies = proxies
        self.last_request_time: float = 0.0

        self.session = requests.Session()
        req_headers = DEFAULT_HEADERS.copy()
        if headers:
            req_headers.update(headers)
        self.session.headers.update(req_headers)

        # Setup retry strategy for transient errors
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _apply_rate_limit(self) -> None:
        """Enforce delay between consecutive requests."""
        if self.delay > 0 and self.last_request_time > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.delay:
                sleep_time = self.delay - elapsed
                time.sleep(sleep_time)

    def get(self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """Execute a GET request with rate limiting and logging."""
        self._apply_rate_limit()
        logger.debug(f"Requesting URL: {url} with params {params}")

        req_kwargs = {
            "timeout": self.timeout,
            "proxies": self.proxies,
            **kwargs,
        }
        if params:
            req_kwargs["params"] = params

        try:
            response = self.session.get(url, **req_kwargs)
            self.last_request_time = time.time()
            return response
        except requests.RequestException as e:
            self.last_request_time = time.time()
            logger.error(f"HTTP GET failed for {url}: {e}")
            raise

    def close(self) -> None:
        """Close the underlying session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
