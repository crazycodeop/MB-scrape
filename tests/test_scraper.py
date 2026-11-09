import pytest
from mb_scrape.constants import normalize_category, CATEGORY_CONFIGS
from mb_scrape.scraper import MagicBricksScraper


def test_normalize_category():
    assert normalize_category("rent") == "residential_rent"
    assert normalize_category("residential-rent") == "residential_rent"
    assert normalize_category("sale") == "residential_sale"
    assert normalize_category("comm_lease") == "commercial_lease"
    assert normalize_category("pg") == "residential_pg"

    with pytest.raises(ValueError):
        normalize_category("non_existent_category")


def test_build_page_url():
    scraper = MagicBricksScraper(delay=0.0)
    
    rent_url = scraper.build_page_url("residential_rent", "Mumbai", 1)
    assert "cityName=Mumbai" in rent_url
    assert "page=1" in rent_url

    sale_url = scraper.build_page_url("residential_sale", "New Delhi", 2)
    assert "flats-in-new-delhi-for-sale-pppfs" in sale_url
    assert "page=2" in sale_url

    comm_sale_url = scraper.build_page_url("commercial_sale", "Pune", 3)
    assert "commercial-property-for-sale-in-pune-pppfs" in comm_sale_url

    comm_rent_url = scraper.build_page_url("commercial_lease", "Bangalore", 1)
    assert "commercial-property-for-rent-in-bangalore-pppfr" in comm_rent_url
