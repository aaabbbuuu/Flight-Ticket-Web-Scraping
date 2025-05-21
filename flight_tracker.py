import logging
import os
import smtplib
from configparser import ConfigParser, NoSectionError, NoOptionError
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# --- Constants ---
CONFIG_FILE = 'config.ini'
ENV_FILE = '.env'

# Placeholder constants for web scraping - ADAPT THESE TO THE TARGET WEBSITE
FLIGHT_SEARCH_URL = 'https://www.example-flight-booking-website.com' # FIXME: Replace with actual URL
# FIXME: Replace with actual selectors for the target website
DEPARTURE_FIELD_ID = 'departure-field-id'
ARRIVAL_FIELD_ID = 'arrival-field-id'
# DATE_PICKER_START_ID = 'date-picker-start-id' # Example
# DATE_PICKER_END_ID = 'date-picker-end-id'     # Example
SEARCH_BUTTON_ID = 'search-button-id'
FLIGHT_RESULTS_CONTAINER_CLASS = 'result-class-name' # A class that appears once results are loaded
PRICE_ELEMENT_CLASS = 'price-class-name' # Class for elements containing price text
INITIAL_LOAD_ELEMENT_ID = 'some-search-box-id' # Element to wait for on initial page load

# --- Configuration ---
@dataclass
class FlightScraperConfig:
    """Holds flight search parameters."""
    start_date: datetime
    end_date: datetime
    price_threshold: int
    departure_code: str
    arrival_code: str

@dataclass
class EmailConfig:
    """Holds email credentials."""
    sender_email: str
    sender_password: str
    recipient_email: str # Can be same as sender for self-notification

def load_configuration() -> Tuple[Optional[FlightScraperConfig], Optional[EmailConfig]]:
    """Loads flight and email configurations."""
    # Load environment variables for email
    load_dotenv(ENV_FILE)
    email_address = os.getenv('FLIGHT_ALERT_EMAIL')
    email_password = os.getenv('FLIGHT_ALERT_PASSWORD')

    if not email_address or not email_password:
        logging.error(f"Email credentials not found in {ENV_FILE}. "
                      "Please set FLIGHT_ALERT_EMAIL and FLIGHT_ALERT_PASSWORD.")
        return None, None
    email_conf = EmailConfig(
        sender_email=email_address,
        sender_password=email_password,
        recipient_email=email_address # Default to sending to self
    )

    # Load flight parameters from config.ini
    config_parser = ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        logging.error(f"{CONFIG_FILE} not found.")
        return None, email_conf # Still return email_conf if it was loaded

    config_parser.read(CONFIG_FILE)

    try:
        start_date_str = config_parser.get('FLIGHTS', 'START_DATE')
        end_date_str = config_parser.get('FLIGHTS', 'END_DATE')
        price_threshold_str = config_parser.get('FLIGHTS', 'PRICE_THRESHOLD')
        departure_code = config_parser.get('FLIGHTS', 'DEPARTURE')
        arrival_code = config_parser.get('FLIGHTS', 'ARRIVAL')

        flight_conf = FlightScraperConfig(
            start_date=datetime.strptime(start_date_str, '%Y-%m-%d'),
            end_date=datetime.strptime(end_date_str, '%Y-%m-%d'),
            price_threshold=int(price_threshold_str),
            departure_code=departure_code,
            arrival_code=arrival_code
        )
        return flight_conf, email_conf
    except (NoSectionError, NoOptionError) as e:
        logging.error(f"Error reading {CONFIG_FILE}: {e}")
    except ValueError as e:
        logging.error(f"Error parsing values in {CONFIG_FILE}: {e}")
    
    return None, email_conf


# --- WebDriver Setup ---
def setup_webdriver() -> Optional[WebDriver]:
    """Sets up and returns a headless Chrome WebDriver instance."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu") # Recommended for headless
    chrome_options.add_argument("--window-size=1920,1080") # Can help with some sites
    chrome_options.add_argument("--no-sandbox") # Often needed in CI/Docker environments
    chrome_options.add_argument("--disable-dev-shm-usage") # " "

    try:
        logging.info("Setting up Chrome WebDriver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logging.info("WebDriver setup successful.")
        return driver
    except WebDriverException as e:
        logging.error(f"WebDriver setup failed: {e}")
        logging.error("Ensure Chrome is installed and ChromeDriver is compatible or accessible.")
        return None

# --- Scraping Logic ---
def scrape_flight_prices(driver: WebDriver, config: FlightScraperConfig) -> List[int]:
    """
    Scrapes flight prices for the configured parameters.
    
    NOTE: This function uses placeholder selectors and a placeholder URL.
    It MUST be adapted to the specific flight booking website you intend to use.
    """
    logging.info(f"Navigating to flight search URL: {FLIGHT_SEARCH_URL}")
    driver.get(FLIGHT_SEARCH_URL)
    scraped_prices: List[int] = []

    try:
        # 1. Wait for the page and initial search elements to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, INITIAL_LOAD_ELEMENT_ID))
        )
        logging.info("Flight search page loaded.")

        # 2. Input departure and arrival locations
        # FIXME: Adapt these selectors and interactions for the target website
        departure_field = driver.find_element(By.ID, DEPARTURE_FIELD_ID)
        departure_field.send_keys(config.departure_code)
        logging.info(f"Entered departure: {config.departure_code}")

        arrival_field = driver.find_element(By.ID, ARRIVAL_FIELD_ID)
        arrival_field.send_keys(config.arrival_code)
        logging.info(f"Entered arrival: {config.arrival_code}")

        # 3. Input dates
        # FIXME: This is highly site-specific. You'll need to inspect the website's
        # date pickers and implement logic to select start_date and end_date.
        logging.warning("Date input logic is a placeholder and needs implementation for the target website.")
        logging.info(f"Target dates: {config.start_date.strftime('%Y-%m-%d')} to {config.end_date.strftime('%Y-%m-%d')}")

        # 4. Click the search button
        # FIXME: Adapt selector
        search_button = driver.find_element(By.ID, SEARCH_BUTTON_ID)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, SEARCH_BUTTON_ID)))
        search_button.click()
        logging.info("Clicked search button.")

        # 5. Wait for search results to load
        # FIXME: Adapt selector for a container that holds all flight results
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, FLIGHT_RESULTS_CONTAINER_CLASS))
        )
        logging.info("Flight results page loaded.")

        # 6. Extract prices
        # FIXME: Adapt selector for individual price elements
        price_elements: List[WebElement] = driver.find_elements(By.CLASS_NAME, PRICE_ELEMENT_CLASS)
        if not price_elements:
            logging.warning("No price elements found. Check selectors or website structure.")
            return []

        for price_element in price_elements:
            price_text = price_element.text
            try:
                # Clean and parse price (e.g., "$1,234.56" -> 1234)
                cleaned_price = price_text.replace('$', '').replace(',', '').split('.')[0]
                if cleaned_price.isdigit():
                    scraped_prices.append(int(cleaned_price))
                else:
                    logging.warning(f"Could not parse price value from text: '{price_text}'")
            except ValueError:
                logging.warning(f"Could not convert cleaned price to int: '{price_text}'")
        
        logging.info(f"Found {len(scraped_prices)} prices: {scraped_prices}")
        return scraped_prices

    except TimeoutException:
        logging.error("Timeout occurred while waiting for an element or page load.")
        logging.error("This could be due to slow network, incorrect selectors, or website changes.")
        # driver.save_screenshot('timeout_error.png') # Helpful for debugging
        # logging.info(f"Screenshot saved to timeout_error.png")
        return []
    except WebDriverException as e:
        logging.error(f"A WebDriver error occurred during scraping: {e}")
        return []

# --- Email Alert ---
def send_email_alert(email_conf: EmailConfig, low_price: int, flight_conf: FlightScraperConfig) -> None:
    """Sends an email notification for the flight price."""
    subject = f"✈️ Flight Price Alert: {flight_conf.departure_code} to {flight_conf.arrival_code} for ${low_price}!"
    body = (
        f"Good news!\n\nA flight from {flight_conf.departure_code} to {flight_conf.arrival_code} "
        f"is available for ${low_price}, which is below your threshold of ${flight_conf.price_threshold}.\n\n"
        f"Search dates: {flight_conf.start_date.strftime('%Y-%m-%d')} to {flight_conf.end_date.strftime('%Y-%m-%d')}\n\n"
        f"Book now (remember to verify this price on the actual website)!\n"
        f"{FLIGHT_SEARCH_URL}" # You might want to add a direct link if possible
    )

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = email_conf.sender_email
    msg['To'] = email_conf.recipient_email

    try:
        logging.info(f"Sending email alert to {email_conf.recipient_email}...")
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_conf.sender_email, email_conf.sender_password)
            server.send_message(msg)
        logging.info("Email alert sent successfully.")
    except smtplib.SMTPAuthenticationError:
        logging.error("SMTP Authentication Error: Failed to login. Check email/password or 'less secure app access' for Gmail.")
    except Exception as e:
        logging.error(f"Failed to send email alert: {e}")

# --- Main Logic ---
def main() -> None:
    """Main function to run the flight tracker."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("Starting flight price tracker...")

    flight_conf, email_conf = load_configuration()

    if not email_conf: # Email config is critical for alerts
        logging.error("Exiting due to missing email configuration.")
        return
    if not flight_conf: # Flight config is critical for scraping
        logging.error("Exiting due to missing or invalid flight configuration.")
        return

    driver = setup_webdriver()
    if not driver:
        logging.error("Exiting due to WebDriver setup failure.")
        return

    try:
        logging.info(
            f"Searching for flights: {flight_conf.departure_code} -> {flight_conf.arrival_code}, "
            f"Dates: {flight_conf.start_date.strftime('%Y-%m-%d')} to {flight_conf.end_date.strftime('%Y-%m-%d')}, "
            f"Price Threshold: ${flight_conf.price_threshold}"
        )
        
        flight_prices = scrape_flight_prices(driver, flight_conf)

        if not flight_prices:
            logging.info("No flight prices were found or scraped.")
        else:
            min_price = min(flight_prices)
            logging.info(f"Minimum price found: ${min_price}")

            if min_price <= flight_conf.price_threshold:
                logging.info(
                    f"Low price found: ${min_price} (Threshold: ${flight_conf.price_threshold}). Sending alert."
                )
                send_email_alert(email_conf, min_price, flight_conf)
            else:
                logging.info(
                    f"Minimum price ${min_price} is above threshold ${flight_conf.price_threshold}. No alert sent."
                )

    except Exception as e:
        logging.critical(f"An unhandled error occurred in the main process: {e}", exc_info=True)
    finally:
        if driver:
            logging.info("Quitting WebDriver.")
            driver.quit()
        logging.info("Flight price tracker finished.")

if __name__ == "__main__":
    main()