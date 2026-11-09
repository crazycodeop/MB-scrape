"""High-level scraper orchestrator for MagicBricks."""

import logging
from typing import List, Dict, Union, Optional, Set
import requests

from mb_scrape.constants import CATEGORY_CONFIGS, DEFAULT_CITIES, normalize_category
from mb_scrape.client import MagicBricksClient
from mb_scrape.models import PropertyListing, PGListing
from mb_scrape.parsers import parse_property_page, parse_pg_page
from mb_scrape.utils import slugify_city
from mb_scrape.exporter import export_csv, export_json, build_default_filename

logger = logging.getLogger(__name__)


class MagicBricksScraper:
    """Orchestrates scraping across MagicBricks categories, cities, and pagination."""

    def __init__(
        self,
        client: Optional[MagicBricksClient] = None,
        delay: float = 1.0,
        timeout: int = 20,
    ):
        self.client = client or MagicBricksClient(delay=delay, timeout=timeout)
        self._owned_client = client is None

    def build_page_url(self, category_key: str, city: str, page: int) -> str:
        """Construct the search URL for category, city, and page number."""
        cfg = CATEGORY_CONFIGS[category_key]
        template = cfg["url_template"]
        city_slug = slugify_city(city)
        return template.format(page=page, city=city, city_slug=city_slug)

    def scrape_category_city(
        self,
        category: str,
        city: str,
        max_pages: int = 1,
    ) -> List[Union[PropertyListing, PGListing]]:
        """
        Scrape listings for a specific category and city across multiple pages.
        Returns deduplicated list of listings.
        """
        category_key = normalize_category(category)
        cfg = CATEGORY_CONFIGS[category_key]
        is_pg = cfg["type"] == "pg"

        all_listings: List[Union[PropertyListing, PGListing]] = []
        seen_keys: Set[str] = set()

        logger.info(f"Starting scrape: {cfg['display_name']} in '{city}' (Pages 1 to {max_pages})")

        for page in range(1, max_pages + 1):
            url = self.build_page_url(category_key, city, page)
            logger.info(f"Scraping page {page}/{max_pages}: {url}")

            try:
                resp = self.client.get(url)
            except requests.RequestException as e:
                logger.error(f"Failed to fetch page {page} for {city}: {e}")
                break

            if resp.status_code != 200:
                logger.warning(f"Received status code {resp.status_code} on page {page} for {city}. Stopping pagination.")
                break

            if "We'll be back soon!" in resp.text:
                logger.warning(f"Received maintenance/block page for {city} on page {page}. Stopping.")
                break

            if is_pg:
                page_items = parse_pg_page(resp.text, city=city)
            else:
                page_items = parse_property_page(resp.text, category=category_key, city=city)

            if not page_items:
                logger.info(f"No cards found on page {page} for {city}. End of results.")
                break

            added_count = 0
            for item in page_items:
                key = item.id or item.url or f"{getattr(item, 'title', '')}_{getattr(item, 'locality', '')}"
                if key and key in seen_keys:
                    continue
                if key:
                    seen_keys.add(key)
                all_listings.append(item)
                added_count += 1

            logger.info(f"Page {page}: Extracted {len(page_items)} cards ({added_count} new, {len(all_listings)} total).")

        return all_listings

    def scrape(
        self,
        categories: Union[str, List[str]],
        cities: Union[str, List[str]],
        max_pages: int = 1,
        export_formats: Optional[List[str]] = None,
        output_dir: str = "output",
    ) -> Dict[str, Dict[str, List[Union[PropertyListing, PGListing]]]]:
        """
        Scrape multiple categories and cities, optionally saving exports.
        Returns nested dictionary: results[category][city] = [listings]
        """
        if isinstance(categories, str):
            if categories.lower() == "all":
                cat_list = list(CATEGORY_CONFIGS.keys())
            else:
                cat_list = [categories]
        else:
            cat_list = categories

        if isinstance(cities, str):
            city_list = [cities]
        else:
            city_list = cities

        results: Dict[str, Dict[str, List[Union[PropertyListing, PGListing]]]] = {}

        for raw_cat in cat_list:
            cat_key = normalize_category(raw_cat)
            results[cat_key] = {}

            for city in city_list:
                listings = self.scrape_category_city(cat_key, city=city, max_pages=max_pages)
                results[cat_key][city] = listings

                if export_formats and listings:
                    if "csv" in export_formats:
                        csv_file = build_default_filename(cat_key, city, "csv", output_dir)
                        export_csv(listings, csv_file)
                    if "json" in export_formats:
                        json_file = build_default_filename(cat_key, city, "json", output_dir)
                        export_json(listings, json_file)

        return results

    def close(self) -> None:
        """Close client session if owned."""
        if self._owned_client:
            self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
