"""Flight price scraping from Google Flights via headless Chrome / Selenium."""

import logging
import re
import time
from typing import List, Optional

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from .config import FlightScraperConfig

logger = logging.getLogger(__name__)

GOOGLE_FLIGHTS_URL = "https://www.google.com/travel/flights"
PRICE_RE = re.compile(r"\$[\d,]+")


def setup_webdriver() -> Optional[WebDriver]:
    """Create a headless Chrome WebDriver instance."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )

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
    """Extract an integer price from a string like '$1,234'."""
    match = PRICE_RE.search(text)
    if not match:
        return None
    try:
        return int(match.group().replace("$", "").replace(",", ""))
    except ValueError:
        return None


def _fill_airport(driver: WebDriver, field_label: str, dialog_label: str, code: str) -> None:
    """Click an airport field, type the code in the dialog, and select the first suggestion."""
    # Click the combobox to open the dialog
    field = driver.find_element(By.CSS_SELECTOR, f'input[aria-label="{field_label}"]')
    driver.execute_script("arguments[0].click();", field)
    time.sleep(0.5)

    # Type into the dialog input
    dialog_input = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, f'[role="dialog"][aria-label="{dialog_label}"] input')
        )
    )
    dialog_input.clear()
    dialog_input.send_keys(code)
    time.sleep(1.5)  # wait for autocomplete suggestions

    # Click the first suggestion
    first_suggestion = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, f'[role="dialog"][aria-label="{dialog_label}"] [role="listbox"] li')
        )
    )
    first_suggestion.click()
    time.sleep(0.5)


def _select_dates(driver: WebDriver, start_iso: str, end_iso: str) -> None:
    """Open the date picker and select departure + return dates."""
    # Click the departure date input to open the calendar
    dep_input = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Departure"]')
    driver.execute_script("arguments[0].click();", dep_input)
    time.sleep(1)

    # Click the departure date in the calendar
    dep_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-iso="{start_iso}"]'))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", dep_btn)
    driver.execute_script("arguments[0].click();", dep_btn)
    time.sleep(0.5)

    # Click the return date
    ret_btn = driver.find_element(By.CSS_SELECTOR, f'[data-iso="{end_iso}"]')
    driver.execute_script("arguments[0].scrollIntoView(true);", ret_btn)
    driver.execute_script("arguments[0].click();", ret_btn)
    time.sleep(0.5)

    # Click the visible "Done" button
    driver.execute_script("""
        const buttons = Array.from(document.querySelectorAll('button'));
        const done = buttons.find(b => b.textContent.trim() === 'Done' && b.offsetParent !== null);
        if (done) { done.scrollIntoView(); done.click(); }
    """)
    time.sleep(1)


def _click_search(driver: WebDriver) -> None:
    """Click the Search button."""
    driver.execute_script("""
        const buttons = Array.from(document.querySelectorAll('button'));
        const btn = buttons.find(b => b.textContent.includes('Search') && b.offsetParent !== null);
        if (btn) btn.click();
    """)


def _extract_prices(driver: WebDriver) -> List[int]:
    """Pull all dollar prices from the results page."""
    prices: List[int] = []
    body_text = driver.find_element(By.TAG_NAME, "body").text
    for match in PRICE_RE.findall(body_text):
        price = _parse_price(match)
        if price is not None and price > 0:
            prices.append(price)
    # Deduplicate while preserving order
    seen = set()
    unique: List[int] = []
    for p in prices:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique


def scrape_flight_prices(driver: WebDriver, config: FlightScraperConfig) -> List[int]:
    """
    Scrape flight prices from Google Flights for the configured route and dates.

    Returns a list of unique integer prices found on the results page.
    """
    logger.info("Navigating to Google Flights…")
    driver.get(GOOGLE_FLIGHTS_URL)

    try:
        # Wait for the search form to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[aria-label="Where from?"]')
            )
        )
        logger.info("Google Flights loaded.")

        # 1. Fill departure airport
        logger.info("Setting departure: %s", config.departure_code)
        _fill_airport(
            driver,
            field_label="Where from?",
            dialog_label="Enter your origin",
            code=config.departure_code,
        )

        # 2. Fill arrival airport
        logger.info("Setting arrival: %s", config.arrival_code)
        _fill_airport(
            driver,
            field_label="Where to? ",  # note trailing space in Google's label
            dialog_label="Enter your destination",
            code=config.arrival_code,
        )

        # 3. Select dates
        start_iso = config.start_date.strftime("%Y-%m-%d")
        end_iso = config.end_date.strftime("%Y-%m-%d")
        logger.info("Selecting dates: %s → %s", start_iso, end_iso)
        _select_dates(driver, start_iso, end_iso)

        # 4. Search
        logger.info("Clicking Search…")
        _click_search(driver)

        # 5. Wait for results to load
        time.sleep(8)  # Google Flights needs time to fetch results
        logger.info("Results page: %s", driver.current_url)

        # 6. Extract prices
        prices = _extract_prices(driver)
        if prices:
            logger.info("Found %d unique prices: %s", len(prices), prices)
        else:
            logger.warning("No prices found — the page may not have loaded results.")

        return prices

    except TimeoutException:
        logger.error("Timeout waiting for page elements.")
        return []
    except (NoSuchElementException, WebDriverException) as exc:
        logger.error("Error during scraping: %s", exc)
        return []
