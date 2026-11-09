import datetime
import pytest
from mb_scrape.utils import (
    slugify_city,
    clean_text,
    clean_price,
    extract_bhk,
    parse_relative_date,
)


def test_slugify_city():
    assert slugify_city("Mumbai") == "mumbai"
    assert slugify_city("New Delhi") == "new-delhi"
    assert slugify_city("Greater-Noida") == "greater-noida"
    assert slugify_city("Navi Mumbai ") == "navi-mumbai"


def test_clean_text():
    assert clean_text("  hello   world  ") == "hello world"
    assert clean_text("Non\xa0breaking   space") == "Non breaking space"
    assert clean_text("") is None
    assert clean_text(None) is None


def test_clean_price():
    assert clean_price("₹4.5 Lac") == "4.5 Lac"
    assert clean_price("₹ 1.20 Cr ") == "1.20 Cr"
    assert clean_price("Rs. 15,000") == "15,000"
    assert clean_price(None) is None


def test_extract_bhk():
    assert extract_bhk("3 BHK Flat for Rent") == "3 BHK"
    assert extract_bhk("Spacious 2.5 bhk apartment") == "2.5 BHK"
    assert extract_bhk("Commercial Office Space") is None
    assert extract_bhk(None) is None


def test_parse_relative_date():
    base = datetime.date(2026, 11, 9)

    assert parse_relative_date("Posted: Today", base_date=base) == "2026-11-09"
    assert parse_relative_date("Yesterday", base_date=base) == "2026-11-08"
    assert parse_relative_date("Posted: 3 days ago", base_date=base) == "2026-11-06"
    assert parse_relative_date("2 weeks ago", base_date=base) == "2026-10-26"
    assert parse_relative_date("1 month ago", base_date=base) == "2026-10-10"
    assert parse_relative_date("15/08/2026", base_date=base) == "2026-08-15"
    assert parse_relative_date(None) is None
