"""Export utilities for CSV, JSON, and DataFrame formats."""

import os
import json
import logging
import datetime
from typing import List, Union, Optional
import pandas as pd

from mb_scrape.models import PropertyListing, PGListing

logger = logging.getLogger(__name__)


def to_dataframe(listings: List[Union[PropertyListing, PGListing]]) -> pd.DataFrame:
    """Convert a list of listing objects into a pandas DataFrame."""
    if not listings:
        return pd.DataFrame()

    data = [item.to_dict() if hasattr(item, "to_dict") else item for item in listings]
    df = pd.DataFrame(data)
    # Deduplicate based on ID or URL if available
    dedup_cols = [c for c in ["id", "url"] if c in df.columns]
    if dedup_cols:
        before = len(df)
        df = df.drop_duplicates(subset=dedup_cols, keep="first")
        after = len(df)
        if before > after:
            logger.info(f"Deduplicated {before - after} duplicate records.")

    return df


def export_csv(
    listings: Union[List[Union[PropertyListing, PGListing]], pd.DataFrame],
    file_path: str,
    index: bool = False,
) -> str:
    """Export listings to CSV file with utf-8-sig encoding for universal Excel compatibility."""
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    if isinstance(listings, pd.DataFrame):
        df = listings
    else:
        df = to_dataframe(listings)

    df.to_csv(file_path, index=index, encoding="utf-8-sig")
    logger.info(f"Saved {len(df)} records to CSV: {file_path}")
    return file_path


def export_json(
    listings: Union[List[Union[PropertyListing, PGListing]], pd.DataFrame],
    file_path: str,
    indent: int = 2,
) -> str:
    """Export listings to formatted JSON file."""
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    if isinstance(listings, pd.DataFrame):
        data = json.loads(listings.to_json(orient="records"))
    else:
        data = [item.to_dict() if hasattr(item, "to_dict") else item for item in listings]

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

    logger.info(f"Saved {len(data)} records to JSON: {file_path}")
    return file_path


def build_default_filename(
    category: str,
    city: Optional[str] = None,
    extension: str = "csv",
    output_dir: str = "output"
) -> str:
    """Generate default timestamped filename in output_dir."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    city_part = f"_{city.lower()}" if city else ""
    cat_clean = category.replace("-", "_")
    filename = f"{cat_clean}{city_part}_{today}.{extension.lstrip('.')}"
    return os.path.join(output_dir, filename)
