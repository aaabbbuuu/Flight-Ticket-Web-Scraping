"""Configuration loading from config.ini and .env files."""

import logging
import os
from configparser import ConfigParser, NoSectionError, NoOptionError
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

CONFIG_FILE = "config.ini"
ENV_FILE = ".env"


@dataclass
class FlightScraperConfig:
    """Flight search parameters."""

    start_date: datetime
    end_date: datetime
    price_threshold: int
    departure_code: str
    arrival_code: str

    def __post_init__(self) -> None:
        if self.start_date > self.end_date:
            raise ValueError("START_DATE must be before END_DATE")
        if self.price_threshold <= 0:
            raise ValueError("PRICE_THRESHOLD must be a positive integer")
        if not self.departure_code or not self.arrival_code:
            raise ValueError("DEPARTURE and ARRIVAL codes must not be empty")


@dataclass
class EmailConfig:
    """Email credentials for sending alerts."""

    sender_email: str
    sender_password: str
    recipient_email: str


def load_email_config(env_file: str = ENV_FILE) -> Optional[EmailConfig]:
    """Load email credentials from .env file."""
    load_dotenv(env_file)
    email_address = os.getenv("FLIGHT_ALERT_EMAIL")
    email_password = os.getenv("FLIGHT_ALERT_PASSWORD")

    if not email_address or not email_password:
        logger.error(
            "Email credentials not found in %s. "
            "Set FLIGHT_ALERT_EMAIL and FLIGHT_ALERT_PASSWORD.",
            env_file,
        )
        return None

    return EmailConfig(
        sender_email=email_address,
        sender_password=email_password,
        recipient_email=email_address,
    )


def load_flight_config(config_file: str = CONFIG_FILE) -> Optional[FlightScraperConfig]:
    """Load flight search parameters from config.ini."""
    if not os.path.exists(config_file):
        logger.error("%s not found.", config_file)
        return None

    parser = ConfigParser()
    parser.read(config_file)

    try:
        flight_conf = FlightScraperConfig(
            start_date=datetime.strptime(
                parser.get("FLIGHTS", "START_DATE"), "%Y-%m-%d"
            ),
            end_date=datetime.strptime(
                parser.get("FLIGHTS", "END_DATE"), "%Y-%m-%d"
            ),
            price_threshold=int(parser.get("FLIGHTS", "PRICE_THRESHOLD")),
            departure_code=parser.get("FLIGHTS", "DEPARTURE"),
            arrival_code=parser.get("FLIGHTS", "ARRIVAL"),
        )
        return flight_conf
    except (NoSectionError, NoOptionError) as e:
        logger.error("Error reading %s: %s", config_file, e)
    except ValueError as e:
        logger.error("Error parsing values in %s: %s", config_file, e)

    return None


def load_configuration(
    config_file: str = CONFIG_FILE, env_file: str = ENV_FILE
) -> Tuple[Optional[FlightScraperConfig], Optional[EmailConfig]]:
    """Load both flight and email configurations."""
    email_conf = load_email_config(env_file)
    flight_conf = load_flight_config(config_file)
    return flight_conf, email_conf
