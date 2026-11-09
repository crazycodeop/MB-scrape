import pytest
import datetime
from mb_scrape.parsers import parse_property_page, parse_pg_page, extract_json_ld_items
from bs4 import BeautifulSoup


SAMPLE_PROPERTY_HTML = """
<html>
<head>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "item": {
        "@type": "Apartment",
        "name": "3 BHK Flat for Rent in Bandra West, Mumbai",
        "url": "https://www.magicbricks.com/propertyDetails/test&id=12345",
        "numberOfBedrooms": 3,
        "numberOfBathroomsTotal": 3,
        "geo": {
          "latitude": 19.0596,
          "longitude": 72.8295
        },
        "address": {
          "addressLocality": "Bandra West",
          "addressRegion": "Mumbai"
        }
      }
    }
  ]
}
</script>
</head>
<body>
  <div class="mb-srp__card">
    <h2 class="mb-srp__card--title">3 BHK Flat for Rent in Bandra West, Mumbai</h2>
    <div class="mb-srp__card__price--amount">₹1.5 Lac</div>
    <div class="mb-srp__card__price--size">₹100 per sqft</div>
    <a class="view-property-link" href="/propertyDetails/test&id=12345">View</a>
    <a class="mb-srp__card__developer--name">Seaside Heights</a>
    <div class="mb-srp__card__ads__info--name">Agent: Dream Homes</div>
    <div class="mb-srp__card__photo__fig--post">Posted: Today</div>
    <div class="mb-srp__card--desc--text"><p>Luxury 3 BHK flat with sea view.</p></div>
    <div class="mb-srp__card__summary__list">
      <div class="mb-srp__card__summary__list--item" data-summary="carpet-area">
        <div class="mb-srp__card__summary--label">Carpet Area</div>
        <div class="mb-srp__card__summary--value">1500 sqft</div>
      </div>
      <div class="mb-srp__card__summary__list--item" data-summary="furnishing">
        <div class="mb-srp__card__summary--label">Furnishing</div>
        <div class="mb-srp__card__summary--value">Furnished</div>
      </div>
      <div class="mb-srp__card__summary__list--item" data-summary="parking">
        <div class="mb-srp__card__summary--label">Car Parking</div>
        <div class="mb-srp__card__summary--value">1 Covered</div>
      </div>
    </div>
  </div>
</body>
</html>
"""

SAMPLE_PG_HTML = """
<html>
<body>
  <div class="m-srp-card">
    <meta itemprop="name" content="Comfort Living PG" />
    <meta itemprop="url" content="/propertyDetail/comfort-living-pg&pgid=99999" />
    <meta itemprop="description" content="Safe and clean PG for boys." />
    <div class="m-srp-card__price">₹12,000 Onwards</div>
    <span class="hidden" 
          data-pgid="99999" 
          data-pgname="Comfort Living PG"
          data-advname="Ramesh"
          data-usertype="Owner"
          data-pglocality="Andheri East"
          data-pgcity="Mumbai"
          data-pgfor="Boys"
          data-minprice="12000"
          data-maxprice="20000"
          data-avail="[Single, Double]">
    </span>
  </div>
</body>
</html>
"""


def test_extract_json_ld_items():
    soup = BeautifulSoup(SAMPLE_PROPERTY_HTML, "html.parser")
    items = extract_json_ld_items(soup)
    assert len(items) >= 1
    assert "12345" in items
    assert items["12345"]["numberOfBedrooms"] == 3


def test_parse_property_page():
    base_date = datetime.date(2026, 11, 9)
    listings = parse_property_page(SAMPLE_PROPERTY_HTML, category="residential_rent", city="Mumbai", today_date=base_date)
    assert len(listings) == 1

    p = listings[0]
    assert p.id == "12345"
    assert p.title == "3 BHK Flat for Rent in Bandra West, Mumbai"
    assert p.bhk == "3 BHK"
    assert p.bedrooms == 3
    assert p.bathrooms == 3
    assert p.price == "1.5 Lac"
    assert p.price_per_sqft == "₹100 per sqft"
    assert p.carpet_area == "1500 sqft"
    assert p.furnishing == "Furnished"
    assert p.car_parking == "1 Covered"
    assert p.society == "Seaside Heights"
    assert p.advertiser_name == "Dream Homes"
    assert p.advertiser_type == "Agent"
    assert p.posted_date == "2026-11-09"
    assert p.latitude == 19.0596
    assert p.longitude == 72.8295
    assert p.locality == "Bandra West"
    assert "https://www.magicbricks.com" in p.url


def test_parse_pg_page():
    listings = parse_pg_page(SAMPLE_PG_HTML, city="Mumbai")
    assert len(listings) == 1

    pg = listings[0]
    assert pg.id == "99999"
    assert pg.name == "Comfort Living PG"
    assert pg.advertiser_name == "Ramesh"
    assert pg.advertiser_type == "Owner"
    assert pg.locality == "Andheri East"
    assert pg.pg_for == "Boys"
    assert pg.min_price == 12000.0
    assert pg.max_price == 20000.0
    assert "comfort-living-pg" in pg.url
