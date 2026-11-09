#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Residential PG (Paying Guest) Scraper (MagicBricks)
Refactored for robust execution, modern URL handling, deduplication, and export.
"""

import os
import sys
import datetime
from mb_scrape.scraper import MagicBricksScraper
from mb_scrape.exporter import export_csv, export_json
from mb_scrape.constants import DEFAULT_CITIES

CITIES = DEFAULT_CITIES[:2]
MAX_PAGES = 1


def scrape(city: str, max_pages: int = MAX_PAGES):
    """Scrape PG listings for the given city."""
    print(f"\n[Scraping Residential PG] City: {city}, Pages: {max_pages}")
    today = datetime.datetime.today().strftime("%Y-%m-%d")

    with MagicBricksScraper(delay=1.0) as scraper:
        listings = scraper.scrape_category_city("residential_pg", city=city, max_pages=max_pages)

    if not listings:
        print(f"[!] No listings found for {city}.")
        return listings

    csv_file = f"{city}_{today}_PG.csv"
    json_file = f"{city}_{today}_PG.json"

    export_csv(listings, csv_file)
    export_json(listings, json_file)

    export_csv(listings, os.path.join("output", csv_file))
    export_json(listings, os.path.join("output", json_file))

    print(f"[SUCCESS] Saved {len(listings)} listings to '{csv_file}' and '{json_file}' (and in 'output/')")
    return listings


def main():
    cities = sys.argv[1:] if len(sys.argv) > 1 else CITIES
    for city in cities:
        scrape(city)


if __name__ == "__main__":
    main()
