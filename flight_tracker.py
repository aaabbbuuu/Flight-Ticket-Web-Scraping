import logging
import os
import smtplib
from datetime import datetime
from configparser import ConfigParser
from email.message import EmailMessage

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load config.ini
config = ConfigParser()
config.read('config.ini')

# Extract values from config
start_date = datetime.strptime(config['FLIGHTS']['START_DATE'], '%Y-%m-%d')
end_date = datetime.strptime(config['FLIGHTS']['END_DATE'], '%Y-%m-%d')
price_threshold = int(config['FLIGHTS']['PRICE_THRESHOLD'])
departure_code = config['FLIGHTS']['DEPARTURE']
arrival_code = config['FLIGHTS']['ARRIVAL']

# Load email credentials from environment
email = os.getenv('FLIGHT_ALERT_EMAIL')
password = os.getenv('FLIGHT_ALERT_PASSWORD')

def setup_webdriver():
    """Sets up a headless Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless")
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        return driver
    except WebDriverException as e:
        logging.error(f"WebDriver setup failed: {e}")
        return None

def scrape_flight_prices(driver):
    """Scrapes flight prices for the configured parameters."""
    url = 'https://www.example-flight-booking-website.com'
    logging.info(f"Navigating to: {url}")
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "some-search-box-id"))
        )

        driver.find_element(By.ID, 'departure-field-id').send_keys(departure_code)
        driver.find_element(By.ID, 'arrival-field-id').send_keys(arrival_code)
        # TODO: Implement logic for entering `start_date` and `end_date`

        driver.find_element(By.ID, 'search-button-id').click()

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "result-class-name"))
        )

        prices = driver.find_elements(By.CLASS_NAME, 'price-class-name')
        return [price.text for price in prices]

    except TimeoutException as e:
        logging.error("Timeout while loading the flight search page.")
        return []

def send_email_alert(low_price):
    """Sends an email notification for the flight price."""
    try:
        msg = EmailMessage()
        msg.set_content(f"Flight price dropped to {low_price}!\nBook now!")
        msg['Subject'] = '🛫 Flight Price Alert'
        msg['From'] = email
        msg['To'] = email

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        server.send_message(msg)
        server.quit()

        logging.info("Email alert sent.")
    except Exception as e:
        logging.error(f"Failed to send email alert: {e}")

def main():
    driver = setup_webdriver()
    if not driver:
        logging.error("Exiting due to WebDriver error.")
        return

    try:
        flight_prices = scrape_flight_prices(driver)
        found = False

        for price_text in flight_prices:
            try:
                price_value = int(price_text.replace('$', '').replace(',', ''))
                if price_value <= price_threshold:
                    logging.info(f"Low price found: ${price_value}")
                    send_email_alert(price_text)
                    found = True
                    break
            except ValueError:
                logging.warning(f"Could not parse price: {price_text}")

        if not found:
            logging.info("No prices below threshold.")

    except Exception as e:
        logging.error(f"Unhandled error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
