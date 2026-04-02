"""Tests for configuration loading."""

import os
import tempfile
from datetime import datetime

import pytest

from flight_tracker.config import (
    FlightScraperConfig,
    load_email_config,
    load_flight_config,
)


class TestFlightScraperConfig:
    def test_valid_config(self):
        config = FlightScraperConfig(
            start_date=datetime(2025, 12, 20),
            end_date=datetime(2025, 12, 30),
            price_threshold=600,
            departure_code="LHE",
            arrival_code="ATL",
        )
        assert config.departure_code == "LHE"

    def test_start_after_end_raises(self):
        with pytest.raises(ValueError, match="START_DATE must be before"):
            FlightScraperConfig(
                start_date=datetime(2025, 12, 30),
                end_date=datetime(2025, 12, 20),
                price_threshold=600,
                departure_code="LHE",
                arrival_code="ATL",
            )

    def test_negative_threshold_raises(self):
        with pytest.raises(ValueError, match="positive integer"):
            FlightScraperConfig(
                start_date=datetime(2025, 12, 20),
                end_date=datetime(2025, 12, 30),
                price_threshold=-1,
                departure_code="LHE",
                arrival_code="ATL",
            )


class TestLoadFlightConfig:
    def test_loads_valid_ini(self, tmp_path):
        ini = tmp_path / "config.ini"
        ini.write_text(
            "[FLIGHTS]\n"
            "START_DATE=2025-12-20\n"
            "END_DATE=2025-12-30\n"
            "PRICE_THRESHOLD=600\n"
            "DEPARTURE=LHE\n"
            "ARRIVAL=ATL\n"
        )
        config = load_flight_config(str(ini))
        assert config is not None
        assert config.departure_code == "LHE"
        assert config.price_threshold == 600

    def test_missing_file_returns_none(self):
        assert load_flight_config("/nonexistent/config.ini") is None


class TestLoadEmailConfig:
    def test_loads_from_env(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text(
            "FLIGHT_ALERT_EMAIL=test@example.com\n"
            "FLIGHT_ALERT_PASSWORD=secret123\n"
        )
        # Clear any existing env vars first
        monkeypatch.delenv("FLIGHT_ALERT_EMAIL", raising=False)
        monkeypatch.delenv("FLIGHT_ALERT_PASSWORD", raising=False)
        config = load_email_config(str(env_file))
        assert config is not None
        assert config.sender_email == "test@example.com"

    def test_missing_vars_returns_none(self, monkeypatch):
        monkeypatch.delenv("FLIGHT_ALERT_EMAIL", raising=False)
        monkeypatch.delenv("FLIGHT_ALERT_PASSWORD", raising=False)
        assert load_email_config("/nonexistent/.env") is None
