"""Flight price scraping via headless Chrome / Selenium."""

import logging
import re
from typing import List, Optional

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from .config import FlightScraperConfig

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Placeholder constants — ADAPT THESE to the target flight-booking website
# ---------------------------------------------------------------------------
FLIGHT_SEARCH_URL = "https://www.example-flight-booking-website.com"  # FIXME
DEPARTURE_FIELD_ID = "departure-field-id"  # FIXME
ARRIVAL_FIELD_ID = "arrival-field-id"  # FIXME
SEARCH_BUTTON_ID = "search-button-id"  # FIXME
FLIGHT_RESULTS_CONTAINER_CLASS = "result-class-name"  # FIXME
PRICE_ELEMENT_CLASS = "price-class-name"  # FIXME
INITIAL_LOAD_ELEMENT_ID = "some-search-box-id"  # FIXME

PRICE_RE = re.compile(r"[\d,]+(?:\.\d{2})?")


def setup_webdriver() -> Optional[WebDriver]:
    """Create a headless Chrome WebDriver instance."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    try:
        logger.info("Setting up Chrome WebDriver…")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("WebDriver ready.")
        return driver
    except WebDriverException as exc:
        logger.error("WebDriver setup failed: %s", exc)
        return None


def _parse_price(text: str) -> Optional[int]:
    """Extract an integer price from a string like '$1,234.56'."""
    text = text.replace("$", "").replace(",", "").strip()
    match = PRICE_RE.search(text)
    if not match:
        return None
    try:
        return int(float(match.group()))
    except ValueError:
        return None


def scrape_flight_prices(
    driver: WebDriver, config: FlightScraperConfig
) -> List[int]:
    """
    Scrape flight prices for the configured route and dates.

    NOTE: Uses placeholder selectors — you MUST adapt them to the target site.
    """
    logger.info("Navigating to %s", FLIGHT_SEARCH_URL)
    driver.get(FLIGHT_SEARCH_URL)
    prices: List[int] = []

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, INITIAL_LOAD_ELEMENT_ID))
        )
        logger.info("Search page loaded.")

        # Departure / arrival
        driver.find_element(By.ID, DEPARTURE_FIELD_ID).send_keys(
            config.departure_code
        )
        driver.find_element(By.ID, ARRIVAL_FIELD_ID).send_keys(
            config.arrival_code
        )
        logger.info(
            "Route: %s → %s", config.departure_code, config.arrival_code
        )

        # Dates — FIXME: implement site-specific date-picker interaction
        logger.warning(
            "Date input is a placeholder — implement for the target site."
        )

        # Search
        btn = driver.find_element(By.ID, SEARCH_BUTTON_ID)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, SEARCH_BUTTON_ID))
        )
        btn.click()
        logger.info("Search submitted.")

        # Wait for results
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, FLIGHT_RESULTS_CONTAINER_CLASS)
            )
        )

        # Extract prices
        for el in driver.find_elements(By.CLASS_NAME, PRICE_ELEMENT_CLASS):
            price = _parse_price(el.text)
            if price is not None:
                prices.append(price)
            else:
                logger.warning("Unparseable price text: '%s'", el.text)

        logger.info("Found %d prices: %s", len(prices), prices)

    except TimeoutException:
        logger.error("Timeout waiting for page elements — check selectors.")
    except WebDriverException as exc:
        logger.error("WebDriver error during scraping: %s", exc)

    return prices
