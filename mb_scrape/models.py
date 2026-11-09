"""Data models for property and PG listings."""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any


@dataclass
class PropertyListing:
    id: Optional[str] = None
    title: Optional[str] = None
    category: Optional[str] = None
    city: Optional[str] = None
    locality: Optional[str] = None
    price: Optional[str] = None
    price_per_sqft: Optional[str] = None
    bhk: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    balconies: Optional[int] = None
    carpet_area: Optional[str] = None
    super_area: Optional[str] = None
    furnishing: Optional[str] = None
    car_parking: Optional[str] = None
    facing: Optional[str] = None
    floor: Optional[str] = None
    status: Optional[str] = None
    society: Optional[str] = None
    advertiser_name: Optional[str] = None
    advertiser_type: Optional[str] = None
    posted_date: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    scraped_at: Optional[str] = None
    extra_details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert listing to dictionary without extra_details nesting if not needed."""
        d = asdict(self)
        # Flatten extra details if any
        extras = d.pop("extra_details", {})
        for k, v in extras.items():
            if k not in d:
                d[k] = v
        return d


@dataclass
class PGListing:
    id: Optional[str] = None
    name: Optional[str] = None
    category: str = "residential_pg"
    city: Optional[str] = None
    locality: Optional[str] = None
    pg_for: Optional[str] = None
    charges: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    deposit: Optional[str] = None
    sharing_options: Optional[str] = None
    advertiser_name: Optional[str] = None
    advertiser_type: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    scraped_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert PG listing to dictionary."""
        return asdict(self)
