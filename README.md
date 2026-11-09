# MB-Scrape 🏠

A high-performance, modular Python scraper for **MagicBricks** real estate and paying guest (PG) property listings across India.

Supports automated extraction of residential properties (rent & sale), commercial properties (lease & sale), and PG accommodations with structured JSON-LD and HTML parsing, duplicate detection, export to CSV/JSON, and polite request throttling.

---

## 🚀 What's New in 2.0 (Refactored)

* **Robust Network & Anti-Bot Engine**: Uses realistic browser headers and an automated retry mechanism (`urllib3.util.retry.Retry`) with exponential backoff and request throttling (`delay=1.0s`) to prevent HTTP 403 / 429 bans.
* **Modernized URL Routing**: Replaced deprecated/broken MagicBricks URL endpoints with current production routing schemes for all categories.
* **Structured Data Fusion**: Extracts both Schema.org JSON-LD metadata (`ItemList`, geo-coordinates, exact bed/bath counts) and rich DOM card attributes (pricing, amenities, societies, advertiser info).
* **Zero Syntax Errors & Memory Leaks**: Fixed Google Colab notebook export artifacts (`pip install ...` statements), global list state leaks across cities, and syntax typos in city lists.
* **Universal CLI & Python SDK**: Use directly via command-line (`python -m mb_scrape`) or as an importable library (`from mb_scrape import MagicBricksScraper`).
* **Multi-Format Export**: Clean exports to both `.csv` (encoded in `utf-8-sig` for immediate Excel compatibility) and formatted `.json`.
* **100% Backward Compatibility**: Legacy scripts (`residential_rent.py`, `residential_sale.py`, `commercial_lease.py`, `commercial_sale.py`, `residential_pg.py`) are fully refactored and work out-of-the-box.

---

## 📦 Installation

Ensure you have Python 3.8+ installed.

```bash
git clone https://github.com/crazycodeop/MB-scrape.git
cd MB-scrape
pip install -r requirements.txt
```

---

## 🛠️ CLI Usage

You can run the scraper directly from your terminal using `python -m mb_scrape` (or `mb-scrape` if installed via `pip install -e .`):

### 1. Scrape Residential Rent listings
```bash
python -m mb_scrape --category residential_rent --cities Mumbai Pune --pages 2
```

### 2. Scrape Residential Sale listings
```bash
python -m mb_scrape --category residential_sale --cities "New Delhi" Bangalore --pages 1
```

### 3. Scrape Commercial Properties (Lease or Sale)
```bash
python -m mb_scrape --category commercial_lease --cities Mumbai --pages 2
python -m mb_scrape --category commercial_sale --cities Hyderabad --pages 1
```

### 4. Scrape Paying Guest (PG) listings
```bash
python -m mb_scrape --category residential_pg --cities Mumbai --pages 1
```

### 5. Scrape All Categories
```bash
python -m mb_scrape --category all --cities Mumbai --pages 1
```

### CLI Options:

| Flag | Description | Default |
|------|-------------|---------|
| `-c`, `--category` | Category: `residential_rent`, `residential_sale`, `commercial_lease`, `commercial_sale`, `residential_pg`, or `all` (aliases like `rent`, `sale`, `pg` accepted) | `residential_rent` |
| `--cities` | List of cities separated by space | `Mumbai` |
| `-p`, `--pages` | Maximum pages to scrape per city | `1` |
| `-d`, `--delay` | Delay in seconds between requests (politeness throttle) | `1.0` |
| `-o`, `--output-dir` | Directory to save output files | `output` |
| `-f`, `--format` | Output format: `csv`, `json`, or `both` | `both` |
| `-v`, `--verbose` | Enable verbose debug logging | `False` |

---

## 💻 Python API Usage

```python
from mb_scrape import MagicBricksScraper

# Initialize scraper with 1.5s delay between requests
with MagicBricksScraper(delay=1.5) as scraper:
    # Scrape listings for a specific category and city
    listings = scraper.scrape_category_city(
        category="residential_rent",
        city="Mumbai",
        max_pages=2
    )

    for item in listings[:5]:
        print(f"Title: {item.title}")
        print(f"Price: {item.price}")
        print(f"BHK: {item.bhk} | Locality: {item.locality}")
        print(f"URL: {item.url}\n")
```

### Exporting Scraped Data:

```python
from mb_scrape.exporter import export_csv, export_json, to_dataframe

# Convert to Pandas DataFrame
df = to_dataframe(listings)
print(df.head())

# Export manually
export_csv(listings, "output/my_listings.csv")
export_json(listings, "output/my_listings.json")
```

---

## 📂 Project Structure

```
MB-scrape/
├── mb_scrape/                 # Core Python package
│   ├── __init__.py           # Package exports and versioning
│   ├── __main__.py           # python -m mb_scrape entrypoint
│   ├── cli.py                # Command-line interface
│   ├── client.py             # HTTP client with retries and session pooling
│   ├── constants.py          # Category endpoints, URLs, default cities
│   ├── exporter.py           # CSV, JSON, and DataFrame exporters
│   ├── models.py             # PropertyListing & PGListing dataclasses
│   ├── parsers.py            # DOM & Schema.org JSON-LD parsers
│   ├── scraper.py            # High-level scraper orchestrator
│   └── utils.py              # Date, price, text normalization helpers
├── tests/                    # Pytest test suite
│   ├── test_utils.py         # Tests for parsing helpers
│   ├── test_parsers.py       # Tests for HTML and schema parsing
│   ├── test_scraper.py       # Tests for URL routing and normalization
│   └── test_exporter.py      # Tests for CSV/JSON exports
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Package configuration
├── residential_rent.py       # Legacy wrapper script
├── residential_sale.py       # Legacy wrapper script
├── commercial_lease.py       # Legacy wrapper script
├── commercial_sale.py        # Legacy wrapper script
├── residential_pg.py         # Legacy wrapper script
└── README.md
```

---

## 🧪 Running Tests

Run the unit test suite using `pytest`:

```bash
pytest
```

---

## ⚖️ License

MIT License. Educational and personal research use only. Please respect MagicBricks' terms of service and robots.txt.
