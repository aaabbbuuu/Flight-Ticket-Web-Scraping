# ✈️ Flight Price Tracker

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Scheduled Check](https://img.shields.io/badge/CI-GitHub%20Actions-orange.svg)](.github/workflows/flight-check.yml)

A Python CLI tool that scrapes flight prices using headless Chrome and sends you an email alert when a deal drops below your threshold. Run it locally, in Docker, or on a schedule via GitHub Actions.

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  config.ini  │────▶│   Selenium   │────▶│  Price Check  │────▶│  Email Alert │
│    + .env    │     │  (headless)  │     │  & CSV Export │     │  (Gmail SMTP)│
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

## Features

- Headless browser scraping with Selenium + auto-managed ChromeDriver
- Configurable search parameters (airports, dates, price threshold)
- Email alerts via Gmail SMTP when prices drop below threshold
- CSV export of scraped results
- `--dry-run` mode to validate config without scraping
- Docker support for containerized execution
- GitHub Actions workflow for automated scheduled checks
- Modular package structure with full type hints

## Quick Start

```bash
# Clone
git clone https://github.com/yourname/flight-price-tracker.git
cd flight-price-tracker

# Install
pip install -r requirements.txt

# Configure
cp config.ini.example config.ini   # edit flight search params
cp .env.example .env               # set email credentials

# Run
python -m flight_tracker
```

## Configuration

### `config.ini`

```ini
[FLIGHTS]
START_DATE=2025-12-20
END_DATE=2025-12-30
PRICE_THRESHOLD=600
DEPARTURE=LHE
ARRIVAL=ATL
```

### `.env`

```env
FLIGHT_ALERT_EMAIL=you@gmail.com
FLIGHT_ALERT_PASSWORD=your-app-password
```

> Gmail users with 2FA enabled must use an [App Password](https://support.google.com/accounts/answer/185833), not their account password.

## Usage

```bash
# Standard run
python -m flight_tracker

# Validate config without scraping
python -m flight_tracker --dry-run

# Export results to CSV
python -m flight_tracker --export-csv

# Verbose logging
python -m flight_tracker --verbose

# Custom config paths
python -m flight_tracker --config /path/to/config.ini --env /path/to/.env

# Show version
python -m flight_tracker --version
```

## Docker

```bash
# Build
docker build -t flight-tracker .

# Run (mount your config files)
docker run --rm \
  -v $(pwd)/config.ini:/app/config.ini \
  -v $(pwd)/.env:/app/.env \
  flight-tracker --export-csv
```

## GitHub Actions (Scheduled Checks)

The included workflow (`.github/workflows/flight-check.yml`) runs every 6 hours and can also be triggered manually.

### Setup

1. Go to your repo's **Settings → Secrets and variables → Actions**
2. Add these **secrets**:
   - `FLIGHT_ALERT_EMAIL` — your Gmail address
   - `FLIGHT_ALERT_PASSWORD` — your Gmail App Password
3. Add these **variables**:
   - `START_DATE` — e.g. `2025-12-20`
   - `END_DATE` — e.g. `2025-12-30`
   - `PRICE_THRESHOLD` — e.g. `600`
   - `DEPARTURE` — e.g. `LHE`
   - `ARRIVAL` — e.g. `ATL`

Results are uploaded as build artifacts and retained for 30 days.

## Project Structure

```
flight-price-tracker/
├── flight_tracker/          # Main package
│   ├── __init__.py          # Version
│   ├── __main__.py          # python -m entry point
│   ├── cli.py               # Argument parsing & orchestration
│   ├── config.py            # Config loading (INI + .env)
│   ├── scraper.py           # Selenium scraping logic
│   ├── alerts.py            # Email alert delivery
│   └── export.py            # CSV export
├── tests/                   # Test suite
│   ├── test_config.py
│   ├── test_scraper.py
│   └── test_export.py
├── .github/workflows/
│   └── flight-check.yml     # Scheduled GitHub Action
├── config.ini.example       # Template for flight params
├── .env.example             # Template for email creds
├── Dockerfile
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── flight_tracker.py        # Legacy single-file entry point
```

## Adapting the Scraper

The scraping logic in `flight_tracker/scraper.py` uses placeholder selectors. To use this with a real flight booking site:

1. Update `FLIGHT_SEARCH_URL` with the target URL
2. Inspect the site's HTML and update the `*_ID` / `*_CLASS` constants with real selectors
3. Implement date-picker interaction in `scrape_flight_prices()` (marked with `FIXME`)

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Contributing

PRs welcome. Please open an issue first to discuss what you'd like to change.

## License

[MIT](LICENSE)
