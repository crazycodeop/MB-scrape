"""MB-Scrape: Modern, modular scraper for MagicBricks real estate listings."""

from mb_scrape.client import MagicBricksClient
from mb_scrape.scraper import MagicBricksScraper
from mb_scrape.models import PropertyListing, PGListing
from mb_scrape.constants import CATEGORY_CONFIGS, DEFAULT_CITIES
from mb_scrape.exporter import export_csv, export_json, to_dataframe

__version__ = "2.0.0"

__all__ = [
    "MagicBricksClient",
    "MagicBricksScraper",
    "PropertyListing",
    "PGListing",
    "CATEGORY_CONFIGS",
    "DEFAULT_CITIES",
    "export_csv",
    "export_json",
    "to_dataframe",
    "__version__",
]
