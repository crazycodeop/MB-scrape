"""Command Line Interface for MB-Scrape."""

import argparse
import sys
import logging

from mb_scrape.constants import CATEGORY_CONFIGS, DEFAULT_CITIES
from mb_scrape.scraper import MagicBricksScraper


def setup_logging(verbose: bool = False):
    """Configure console logging level and format."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    """CLI entry point for mb_scrape."""
    parser = argparse.ArgumentParser(
        prog="mb-scrape",
        description="A robust, modular scraper for MagicBricks real estate listings.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-c", "--category",
        default="residential_rent",
        help=(
            f"Category to scrape: {', '.join(CATEGORY_CONFIGS.keys())}, or 'all'. "
            "Aliases like 'rent', 'sale', 'pg', 'commercial_rent' are also accepted."
        ),
    )

    parser.add_argument(
        "--cities",
        nargs="+",
        default=["Mumbai"],
        help="One or more cities to scrape (e.g. --cities Mumbai Bangalore Pune)",
    )

    parser.add_argument(
        "-p", "--pages",
        type=int,
        default=1,
        help="Maximum number of pages to scrape per city",
    )

    parser.add_argument(
        "-d", "--delay",
        type=float,
        default=1.0,
        help="Delay in seconds between consecutive requests",
    )

    parser.add_argument(
        "-o", "--output-dir",
        default="output",
        help="Directory to save scraped CSV / JSON files",
    )

    parser.add_argument(
        "-f", "--format",
        choices=["csv", "json", "both"],
        default="both",
        help="Output export format",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable detailed debug logging",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    export_formats = ["csv", "json"] if args.format == "both" else [args.format]

    print(f"\n=======================================================")
    print(f"  MagicBricks Scraper CLI")
    print(f"  Category:   {args.category}")
    print(f"  Cities:     {', '.join(args.cities)}")
    print(f"  Pages/city: {args.pages}")
    print(f"  Formats:    {', '.join(export_formats)}")
    print(f"  Output Dir: {args.output_dir}")
    print(f"=======================================================\n")

    try:
        with MagicBricksScraper(delay=args.delay) as scraper:
            results = scraper.scrape(
                categories=args.category,
                cities=args.cities,
                max_pages=args.pages,
                export_formats=export_formats,
                output_dir=args.output_dir,
            )

        total_scraped = sum(
            len(listings)
            for city_dict in results.values()
            for listings in city_dict.values()
        )
        print(f"\n[SUCCESS] Scraping completed successfully! Total listings scraped: {total_scraped}")
        print(f"Results saved in '{args.output_dir}/'\n")

    except KeyboardInterrupt:
        print("\n[ABORTED] Scraping interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
