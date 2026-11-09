"""Utility functions for parsing dates, text cleaning, and URL formatting."""

import re
import datetime
from typing import Optional


def slugify_city(city: str) -> str:
    """Format city name into a URL-friendly slug (e.g. 'New-Delhi' -> 'new-delhi')."""
    cleaned = city.strip().lower()
    cleaned = re.sub(r"[\s_]+", "-", cleaned)
    return cleaned


def clean_text(text: Optional[str]) -> Optional[str]:
    """Clean and normalize scraped string text."""
    if not text:
        return None
    # Replace non-breaking spaces and collapse whitespace
    normalized = re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()
    return normalized if normalized else None


def parse_relative_date(
    date_str: Optional[str],
    base_date: Optional[datetime.date] = None,
    output_format: str = "%Y-%m-%d"
) -> Optional[str]:
    """
    Parse MagicBricks posted date string into a standardized date string.
    Handles 'Today', 'Yesterday', 'X days ago', 'X weeks ago', 'X months ago',
    or direct date formats like '12/10/2023'.
    """
    if not date_str:
        return None

    raw = clean_text(date_str)
    if not raw:
        return None

    # Remove 'Posted:' prefix
    raw = re.sub(r"^posted\s*:\s*", "", raw, flags=re.IGNORECASE).strip()

    if base_date is None:
        base_date = datetime.date.today()

    lower = raw.lower()

    if "today" in lower:
        return base_date.strftime(output_format)

    if "yesterday" in lower:
        return (base_date - datetime.timedelta(days=1)).strftime(output_format)

    # Check for 'ago' patterns
    ago_match = re.search(r"(\d+)\s*(day|week|month|year)s?\s*ago", lower)
    if ago_match:
        count = int(ago_match.group(1))
        unit = ago_match.group(2)
        if unit == "day":
            delta = datetime.timedelta(days=count)
        elif unit == "week":
            delta = datetime.timedelta(days=count * 7)
        elif unit == "month":
            delta = datetime.timedelta(days=count * 30)
        elif unit == "year":
            delta = datetime.timedelta(days=count * 365)
        else:
            delta = datetime.timedelta(days=count)
        return (base_date - delta).strftime(output_format)

    # Check if it's already a date like 'DD/MM/YYYY' or 'YYYY-MM-DD'
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%b %d, '%y", "%b %d, %Y"):
        try:
            dt = datetime.datetime.strptime(raw, fmt).date()
            return dt.strftime(output_format)
        except ValueError:
            continue

    return raw


def extract_bhk(text: Optional[str]) -> Optional[str]:
    """Extract BHK specification from title or string (e.g. '2 BHK', '3.5 BHK')."""
    if not text:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)\s*BHK", text, re.IGNORECASE)
    if match:
        return f"{match.group(1)} BHK"
    return None


def clean_price(price_str: Optional[str]) -> Optional[str]:
    """Clean price text, removing ₹ symbols and extra whitespace."""
    if not price_str:
        return None
    cleaned = price_str.replace("₹", "").replace("Rs.", "").replace("Rs", "").strip()
    return clean_text(cleaned)
