"""Constants, URLs, and default configurations for MagicBricks scraper."""

from typing import Dict, List, Any

DEFAULT_HEADERS: Dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

# Supported categories with URL templates and parsing types
CATEGORY_CONFIGS: Dict[str, Dict[str, Any]] = {
    "residential_rent": {
        "display_name": "Residential Rent",
        "type": "standard",
        "url_template": "https://www.magicbricks.com/property-for-rent/residential-commercial-real-estate?page={page}&cityName={city}&language=en",
        "aliases": ["rent", "res_rent", "residential-rent"],
    },
    "residential_sale": {
        "display_name": "Residential Sale",
        "type": "standard",
        "url_template": "https://www.magicbricks.com/flats-in-{city_slug}-for-sale-pppfs?page={page}",
        "aliases": ["sale", "res_sale", "residential-sale", "buy"],
    },
    "commercial_lease": {
        "display_name": "Commercial Lease",
        "type": "standard",
        "url_template": "https://www.magicbricks.com/commercial-property-for-rent-in-{city_slug}-pppfr?page={page}",
        "aliases": ["commercial_rent", "comm_lease", "comm_rent", "commercial-lease", "commercial-rent"],
    },
    "commercial_sale": {
        "display_name": "Commercial Sale",
        "type": "standard",
        "url_template": "https://www.magicbricks.com/commercial-property-for-sale-in-{city_slug}-pppfs?page={page}",
        "aliases": ["comm_sale", "commercial-sale"],
    },
    "residential_pg": {
        "display_name": "Residential PG",
        "type": "pg",
        "url_template": "https://www.magicbricks.com/property-for-rent/residential-paying-guest?cityName={city}&page={page}",
        "aliases": ["pg", "paying_guest", "residential-pg"],
    },
}

# Cleaned list of major Indian cities
DEFAULT_CITIES: List[str] = [
    "Mumbai", "Bangalore", "Pune", "Hyderabad", "New-Delhi",
    "Gurgaon", "Noida", "Ghaziabad", "Greater-Noida", "Thane",
    "Navi-Mumbai", "Chennai", "Kolkata", "Ahmedabad", "Faridabad",
    "Bhubaneswar", "Bokaro-Steel-City", "Vijayawada", "Vrindavan", "Bhopal",
    "Gorakhpur", "Jamshedpur", "Agra", "Allahabad", "Jodhpur",
    "Aurangabad", "Jaipur", "Mangalore", "Nagpur", "Guntur",
    "Navsari", "Palghar", "Salem", "Haridwar", "Durgapur",
    "Madurai", "Manipal", "Patna", "Ranchi", "Raipur",
    "Sonipat", "Kottayam", "Kozhikode", "Thrissur", "Tirupati",
    "Trivandrum", "Trichy", "Udaipur", "Vapi", "Varanasi",
    "Vadodara", "Visakhapatnam", "Surat", "Kanpur", "Kochi",
    "Mysore", "Goa", "Bhiwadi", "Lucknow", "Nashik",
    "Guwahati", "Chandigarh", "Indore", "Coimbatore", "Dehradun",
]

def normalize_category(category_name: str) -> str:
    """Resolve category name or alias to canonical category key."""
    norm = category_name.strip().lower().replace("-", "_")
    for key, cfg in CATEGORY_CONFIGS.items():
        if norm == key or norm in [a.replace("-", "_") for a in cfg["aliases"]]:
            return key
    raise ValueError(f"Unknown category '{category_name}'. Valid categories: {list(CATEGORY_CONFIGS.keys())}")
