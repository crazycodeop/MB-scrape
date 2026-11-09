"""HTML and JSON-LD parsers for MagicBricks search results."""

import re
import json
import logging
import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

from mb_scrape.models import PropertyListing, PGListing
from mb_scrape.utils import clean_text, clean_price, parse_relative_date, extract_bhk

logger = logging.getLogger(__name__)


def extract_json_ld_items(soup: BeautifulSoup) -> Dict[str, Dict[str, Any]]:
    """
    Extract schema.org ItemList data embedded in the HTML page.
    Returns a dictionary keyed by both URL and listing ID for fast lookup.
    """
    lookup: Dict[str, Dict[str, Any]] = {}
    script_tags = soup.find_all("script", type="application/ld+json")

    for tag in script_tags:
        if not tag.string:
            continue
        try:
            data = json.loads(tag.string)
            if isinstance(data, dict) and data.get("@type") == "ItemList":
                items = data.get("itemListElement", [])
                for entry in items:
                    item = entry.get("item", {})
                    if not isinstance(item, dict):
                        continue
                    item_url = item.get("url") or item.get("@id")
                    if item_url:
                        lookup[item_url] = item
                        # Also index by property ID if present in URL
                        id_match = re.search(r"id=([a-zA-Z0-9]+)", item_url)
                        if id_match:
                            lookup[id_match.group(1)] = item
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            logger.debug(f"Failed parsing JSON-LD script tag: {e}")
            continue

    return lookup


def parse_standard_card(
    card,
    category: str,
    city: str,
    json_ld_map: Dict[str, Dict[str, Any]],
    today_date: Optional[datetime.date] = None
) -> Optional[PropertyListing]:
    """Parse a single div.mb-srp__card into a PropertyListing."""
    try:
        # Title
        title_tag = card.find(class_="mb-srp__card--title")
        title = clean_text(title_tag.text) if title_tag else None

        # Link and Property ID
        link_tag = card.find("a", class_="view-property-link") or card.find("a", href=re.compile(r"propertyDetails"))
        url = None
        prop_id = None
        if link_tag and link_tag.get("href"):
            raw_href = link_tag.get("href").strip()
            if raw_href.startswith("http"):
                url = raw_href
            else:
                url = "https://www.magicbricks.com" + ("" if raw_href.startswith("/") else "/") + raw_href

            id_match = re.search(r"id=([a-zA-Z0-9]+)", url)
            if id_match:
                prop_id = id_match.group(1)

        # Price and Price per sqft
        price_tag = card.find("div", class_="mb-srp__card__price--amount")
        price = clean_price(price_tag.text) if price_tag else None

        price_size_tag = card.find("div", class_="mb-srp__card__price--size")
        price_per_sqft = clean_text(price_size_tag.text) if price_size_tag else None

        # Society / Project name
        society_tag = card.find(class_="mb-srp__card__developer--name")
        society = clean_text(society_tag.text) if society_tag else None

        # Advertiser / Owner info
        advertiser_tag = (
            card.find("div", class_="mb-srp__card__ads__info--name")
            or card.find("div", class_="mb-srp__card__ads--name")
        )
        adv_raw = clean_text(advertiser_tag.text) if advertiser_tag else None
        advertiser_type = None
        advertiser_name = adv_raw

        if adv_raw:
            if ":" in adv_raw:
                parts = adv_raw.split(":", 1)
                advertiser_type = parts[0].strip()
                advertiser_name = parts[1].strip()
            elif "owner" in adv_raw.lower():
                advertiser_type = "Owner"
            elif "agent" in adv_raw.lower():
                advertiser_type = "Agent"
            elif "builder" in adv_raw.lower():
                advertiser_type = "Builder"

        # Posted date
        posted_tag = card.find(class_="mb-srp__card__photo__fig--post")
        posted_date = parse_relative_date(posted_tag.text, base_date=today_date) if posted_tag else None

        # Description
        desc_tag = card.find("div", class_="mb-srp__card--desc--text") or card.find("div", class_="mb-srp__card--desc")
        description = None
        if desc_tag:
            p_tag = desc_tag.find("p")
            description = clean_text(p_tag.text if p_tag else desc_tag.text)

        # Summary list items
        summary_data: Dict[str, str] = {}
        for item in card.find_all(class_="mb-srp__card__summary__list--item"):
            val_tag = item.find(class_="mb-srp__card__summary--value")
            lbl_tag = item.find(class_="mb-srp__card__summary--label")
            key = item.get("data-summary")
            if not key and lbl_tag:
                key = clean_text(lbl_tag.text).lower()

            if key and val_tag:
                summary_data[key] = clean_text(val_tag.text)

        carpet_area = summary_data.get("carpet-area")
        super_area = summary_data.get("super-area")
        furnishing = summary_data.get("furnishing")
        car_parking = summary_data.get("parking") or summary_data.get("car-parking")
        facing = summary_data.get("facing")
        floor = summary_data.get("floor")
        status = summary_data.get("status")
        overlooking = summary_data.get("overlooking")
        if not society and summary_data.get("society"):
            society = summary_data.get("society")

        # Parse bathrooms / balconies from summary if present
        bathrooms = None
        if "bathroom" in summary_data:
            b_val = re.search(r"\d+", summary_data["bathroom"])
            if b_val:
                bathrooms = int(b_val.group(0))

        balconies = None
        if "balcony" in summary_data:
            balc_val = re.search(r"\d+", summary_data["balcony"])
            if balc_val:
                balconies = int(balc_val.group(0))

        # BHK extraction
        bhk = extract_bhk(title)
        bedrooms = None
        if bhk:
            b_match = re.search(r"\d+", bhk)
            if b_match:
                bedrooms = int(b_match.group(0))

        # Locality fallback extraction from title
        locality = None
        if title:
            # Common title formats: 'X BHK Flat for Rent in <Locality>, <City>'
            in_match = re.search(r"\sin\s+(.+)$", title, re.IGNORECASE)
            if in_match:
                after_in = in_match.group(1).strip()
                # Split parts: e.g. "Lodha World Crest, Lower Parel, Mumbai"
                loc_parts = [p.strip() for p in after_in.split(",") if p.strip()]
                # Exclude city from end if present
                if loc_parts and loc_parts[-1].lower() == city.lower():
                    loc_parts.pop()
                if loc_parts:
                    locality = ", ".join(loc_parts)

        # Merge with JSON-LD metadata if available
        matched_ld = None
        if url and url in json_ld_map:
            matched_ld = json_ld_map[url]
        elif prop_id and prop_id in json_ld_map:
            matched_ld = json_ld_map[prop_id]

        latitude = None
        longitude = None
        image_url = None

        if matched_ld:
            # Bed/Bathrooms from JSON-LD
            if bedrooms is None and "numberOfBedrooms" in matched_ld:
                bedrooms = matched_ld.get("numberOfBedrooms")
                if not bhk and bedrooms:
                    bhk = f"{bedrooms} BHK"
            if bathrooms is None and "numberOfBathroomsTotal" in matched_ld:
                bathrooms = matched_ld.get("numberOfBathroomsTotal")

            # Geo coordinates
            geo = matched_ld.get("geo")
            if isinstance(geo, dict):
                latitude = geo.get("latitude")
                longitude = geo.get("longitude")

            # Structured address locality
            address = matched_ld.get("address")
            if isinstance(address, dict) and address.get("addressLocality"):
                locality = address.get("addressLocality")

            # Image
            image_url = matched_ld.get("image")

            # Seller name fallback
            if not advertiser_name:
                seller = matched_ld.get("potentialAction", {}).get("seller", {})
                if isinstance(seller, dict) and seller.get("name"):
                    advertiser_name = seller.get("name")
                    advertiser_type = seller.get("@type", advertiser_type)

            # Floor size fallback
            floor_size = matched_ld.get("floorSize")
            if isinstance(floor_size, dict) and not carpet_area and not super_area:
                val = floor_size.get("value")
                if val:
                    carpet_area = f"{val} sqft"

        return PropertyListing(
            id=prop_id,
            title=title,
            category=category,
            city=city,
            locality=locality,
            price=price,
            price_per_sqft=price_per_sqft,
            bhk=bhk,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            balconies=balconies,
            carpet_area=carpet_area,
            super_area=super_area,
            furnishing=furnishing,
            car_parking=car_parking,
            facing=facing,
            floor=floor,
            status=status,
            society=society,
            advertiser_name=advertiser_name,
            advertiser_type=advertiser_type,
            posted_date=posted_date,
            latitude=latitude,
            longitude=longitude,
            url=url,
            image_url=image_url,
            description=description,
            scraped_at=datetime.datetime.now().isoformat(),
            extra_details={
                k: v for k, v in summary_data.items()
                if k not in ["carpet-area", "super-area", "furnishing", "parking", "facing", "floor", "status", "society", "bathroom", "balcony"]
            }
        )
    except Exception as e:
        logger.warning(f"Error parsing property card: {e}")
        return None


def parse_property_page(
    html: str,
    category: str,
    city: str,
    today_date: Optional[datetime.date] = None
) -> List[PropertyListing]:
    """Parse all property cards on a search results page."""
    soup = BeautifulSoup(html, "html.parser")
    json_ld_map = extract_json_ld_items(soup)

    cards = soup.find_all("div", class_="mb-srp__card")
    results: List[PropertyListing] = []

    for card in cards:
        listing = parse_standard_card(card, category, city, json_ld_map, today_date)
        if listing:
            results.append(listing)

    # Fallback: if cards were not rendered or class changed, but JSON-LD exists
    if not results and json_ld_map:
        logger.info(f"Extracting {len(json_ld_map)} listings directly from JSON-LD schema fallback.")
        seen_ids = set()
        for key, item in json_ld_map.items():
            item_url = item.get("url") or item.get("@id")
            if not item_url or item_url in seen_ids:
                continue
            seen_ids.add(item_url)
            prop_id = None
            id_match = re.search(r"id=([a-zA-Z0-9]+)", item_url)
            if id_match:
                prop_id = id_match.group(1)

            geo = item.get("geo", {}) if isinstance(item.get("geo"), dict) else {}
            addr = item.get("address", {}) if isinstance(item.get("address"), dict) else {}
            seller = item.get("potentialAction", {}).get("seller", {}) if isinstance(item.get("potentialAction"), dict) else {}

            bedrooms = item.get("numberOfBedrooms")
            bhk = f"{bedrooms} BHK" if bedrooms else None

            listing = PropertyListing(
                id=prop_id,
                title=clean_text(item.get("name")),
                category=category,
                city=city,
                locality=clean_text(addr.get("addressLocality")),
                bhk=bhk,
                bedrooms=bedrooms,
                bathrooms=item.get("numberOfBathroomsTotal"),
                latitude=geo.get("latitude"),
                longitude=geo.get("longitude"),
                url=item_url,
                image_url=item.get("image"),
                advertiser_name=seller.get("name"),
                advertiser_type=seller.get("@type"),
                scraped_at=datetime.datetime.now().isoformat()
            )
            results.append(listing)

    return results


def parse_pg_card(card, city: str) -> Optional[PGListing]:
    """Parse a single div.m-srp-card into a PGListing."""
    try:
        # Check hidden data cache first
        hidden_span = card.find("span", class_="hidden")
        cache_data = {}
        if hidden_span:
            cache_data = hidden_span.attrs

        pg_id = cache_data.get("data-pgid")
        pg_name = cache_data.get("data-pgname")
        if not pg_name:
            name_meta = card.find("meta", attrs={"itemprop": "name"})
            if name_meta and name_meta.get("content"):
                pg_name = clean_text(name_meta.get("content"))

        advertiser_name = cache_data.get("data-advname")
        advertiser_type = cache_data.get("data-usertype")
        locality = cache_data.get("data-pglocality")
        pg_for = cache_data.get("data-pgfor")

        # Gender fallback
        if not pg_for:
            gender_span = card.find("span", class_="m-srp-card__info__gender")
            if gender_span:
                pg_for = clean_text(gender_span.text)

        # Price
        price_tag = card.find("div", class_="m-srp-card__price")
        charges = clean_price(price_tag.text) if price_tag else None

        min_price = None
        max_price = None
        if cache_data.get("data-minprice"):
            try:
                min_price = float(cache_data["data-minprice"])
            except ValueError:
                pass
        if cache_data.get("data-maxprice"):
            try:
                max_price = float(cache_data["data-maxprice"])
            except ValueError:
                pass

        # Sharing options
        sharing_options = cache_data.get("data-avail")

        # Link
        url = None
        url_meta = card.find("meta", attrs={"itemprop": "url"})
        if url_meta and url_meta.get("content"):
            url = url_meta.get("content")
        elif cache_data.get("data-pgurl"):
            url = cache_data.get("data-pgurl")

        if url and not url.startswith("http"):
            url = "https://www.magicbricks.com/" + url.lstrip("/")

        # Description
        desc_meta = card.find("meta", attrs={"itemprop": "description"})
        description = clean_text(desc_meta.get("content")) if desc_meta else None

        return PGListing(
            id=pg_id,
            name=pg_name,
            city=city,
            locality=locality,
            pg_for=pg_for,
            charges=charges,
            min_price=min_price,
            max_price=max_price,
            sharing_options=sharing_options,
            advertiser_name=advertiser_name,
            advertiser_type=advertiser_type,
            url=url,
            description=description,
            scraped_at=datetime.datetime.now().isoformat()
        )
    except Exception as e:
        logger.warning(f"Error parsing PG card: {e}")
        return None


def parse_pg_page(html: str, city: str) -> List[PGListing]:
    """Parse all PG cards on a paying guest search results page."""
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("div", class_="m-srp-card")
    results: List[PGListing] = []

    for card in cards:
        listing = parse_pg_card(card, city)
        if listing:
            results.append(listing)

    return results
