"""Command-line interface for Flight Price Tracker."""

import argparse
import logging
import sys

from . import __version__
from .alerts import send_email_alert
from .config import load_configuration
from .export import export_prices_csv
from .scraper import scrape_flight_prices, setup_webdriver

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flight-tracker",
        description="Scrape flight prices and get email alerts for deals.",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--config",
        default="config.ini",
        help="Path to config.ini (default: config.ini)",
    )
    parser.add_argument(
        "--env",
        default=".env",
        help="Path to .env file (default: .env)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and exit without scraping or emailing.",
    )
    parser.add_argument(
        "--export-csv",
        action="store_true",
        help="Export scraped prices to a CSV file in results/.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG-level logging.",
    )
    return parser


def main(argv: list | None = None) -> int:
    """Entry point. Returns 0 on success, 1 on failure."""
    args = build_parser().parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    flight_conf, email_conf = load_configuration(args.config, args.env)

    if not email_conf:
        logger.error("Missing email configuration — exiting.")
        return 1
    if not flight_conf:
        logger.error("Missing or invalid flight configuration — exiting.")
        return 1

    logger.info(
        "Config OK — %s → %s, %s to %s, threshold $%d",
        flight_conf.departure_code,
        flight_conf.arrival_code,
        flight_conf.start_date.strftime("%Y-%m-%d"),
        flight_conf.end_date.strftime("%Y-%m-%d"),
        flight_conf.price_threshold,
    )

    if args.dry_run:
        logger.info("Dry run — config validated, nothing else to do.")
        return 0

    driver = setup_webdriver()
    if not driver:
        logger.error("WebDriver setup failed — exiting.")
        return 1

    try:
        prices = scrape_flight_prices(driver, flight_conf)

        if not prices:
            logger.info("No prices found.")
            return 0

        if args.export_csv:
            export_prices_csv(prices, flight_conf)

        min_price = min(prices)
        logger.info("Lowest price: $%d", min_price)

        if min_price <= flight_conf.price_threshold:
            logger.info(
                "$%d ≤ $%d threshold — sending alert.",
                min_price,
                flight_conf.price_threshold,
            )
            send_email_alert(email_conf, min_price, flight_conf)
        else:
            logger.info(
                "$%d > $%d threshold — no alert.",
                min_price,
                flight_conf.price_threshold,
            )

    except Exception as exc:
        logger.critical("Unhandled error: %s", exc, exc_info=True)
        return 1
    finally:
        driver.quit()
        logger.info("Done.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
