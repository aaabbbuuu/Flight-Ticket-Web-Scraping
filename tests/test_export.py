"""Tests for CSV export."""

import csv
from datetime import datetime

from flight_tracker.config import FlightScraperConfig
from flight_tracker.export import export_prices_csv


class TestExportCSV:
    def test_creates_csv(self, tmp_path):
        config = FlightScraperConfig(
            start_date=datetime(2025, 12, 20),
            end_date=datetime(2025, 12, 30),
            price_threshold=600,
            departure_code="LHE",
            arrival_code="ATL",
        )
        path = export_prices_csv([500, 350, 700], config, str(tmp_path))
        assert path.endswith(".csv")

        with open(path, encoding="utf-8") as f:
            reader = list(csv.reader(f))
        # header + 3 data rows
        assert len(reader) == 4
        assert reader[0][0] == "departure"
        # prices should be sorted
        assert reader[1][4] == "350"
