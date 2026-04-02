"""CSV export of scraped flight prices."""

import csv
import logging
import os
from datetime import datetime
from typing import List

from .config import FlightScraperConfig

logger = logging.getLogger(__name__)

RESULTS_DIR = "results"


def export_prices_csv(
    prices: List[int], config: FlightScraperConfig, output_dir: str = RESULTS_DIR
) -> str:
    """Write prices to a timestamped CSV file. Returns the file path."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = (
        f"{config.departure_code}_{config.arrival_code}_{timestamp}.csv"
    )
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            ["departure", "arrival", "start_date", "end_date", "price", "scraped_at"]
        )
        now = datetime.now().isoformat()
        for price in sorted(prices):
            writer.writerow(
                [
                    config.departure_code,
                    config.arrival_code,
                    config.start_date.strftime("%Y-%m-%d"),
                    config.end_date.strftime("%Y-%m-%d"),
                    price,
                    now,
                ]
            )

    logger.info("Exported %d prices to %s", len(prices), filepath)
    return filepath
