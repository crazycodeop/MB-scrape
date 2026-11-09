import os
import json
import pytest
import pandas as pd
from mb_scrape.models import PropertyListing
from mb_scrape.exporter import to_dataframe, export_csv, export_json


def test_to_dataframe_and_deduplication():
    item1 = PropertyListing(id="1", title="Title 1", city="Mumbai")
    item2 = PropertyListing(id="2", title="Title 2", city="Mumbai")
    item3 = PropertyListing(id="1", title="Duplicate 1", city="Mumbai")

    df = to_dataframe([item1, item2, item3])
    assert len(df) == 2
    assert set(df["id"]) == {"1", "2"}


def test_export_csv_and_json(tmp_path):
    item = PropertyListing(id="101", title="Luxury Villa", price="5 Cr", city="Goa")

    csv_path = str(tmp_path / "test.csv")
    json_path = str(tmp_path / "test.json")

    export_csv([item], csv_path)
    export_json([item], json_path)

    assert os.path.exists(csv_path)
    assert os.path.exists(json_path)

    # Read back CSV
    df = pd.read_csv(csv_path)
    assert len(df) == 1
    assert df.iloc[0]["id"] == 101

    # Read back JSON
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["id"] == "101"
