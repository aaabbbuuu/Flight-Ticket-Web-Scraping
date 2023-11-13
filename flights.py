import logging
import configparser
import smtplib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuring logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Read configuration from file
config = configparser.ConfigParser()
config.read('config.ini')

# Extracting configuration values
start_date = config['FLIGHTS']['START_DATE']
end_date = config['FLIGHTS']['END_DATE']
price_threshold = int(config['FLIGHTS']['PRICE_THRESHOLD'])
email = config['EMAIL']['ADDRESS']
password = config['EMAIL']['PASSWORD']

def setup_webdriver():
    """Sets up the Selenium WebDriver with Chrome options."""
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless")
    try:
        driver = webdriver.Chrome(executable_path='D:\Abu Hassan\Documents\ChromeDriver\chromedriver.exe', options=chrome_options)
        return driver
    except WebDriverException as e:
        logging.error(f"Error setting up WebDriver: {e}")
        return None

def scrape_flight_prices(driver, start_date, end_date):
    """Scrapes flight prices for the given date range."""
    url = 'https://www.example-flight-booking-website.com'
    driver.get(url)

    # Wait for the search page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "some-search-box-id"))
    )

    # Find and fill the departure and arrival fields, dates, etc.
    departure_field = driver.find_element(By.ID, 'departure-field-id')
    departure_field.clear()
    departure_field.send_keys('LHE')  # Example departure airport code

    arrival_field = driver.find_element(By.ID, 'arrival-field-id')
    arrival_field.clear()
    arrival_field.send_keys('ATL')  # Example arrival airport code

    # Similarly, find and fill the date fields
    # Note: Date selection will depend on how the website handles date inputs

    # Submit the search
    search_button = driver.find_element(By.ID, 'search-button-id')
    search_button.click()

    # Wait for search results to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "result-class-name"))
    )

    # Extract flight prices
    prices = driver.find_elements(By.CLASS_NAME, 'price-class-name')
    flight_prices = [price.text for price in prices]

    return flight_prices

def send_email_alert(email, password, message):
    """Sends an email alert with the given message."""
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, email, message)
        server.quit()
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

def main():
    driver = setup_webdriver()
    if driver:
        try:
            # Scrape flight prices for the configured date range
            flight_prices = scrape_flight_prices(driver, start_date, end_date)

            # Check if any scraped prices are below the threshold
            for price in flight_prices:
                # Assuming prices are returned as strings like "$500"
                numeric_price = int(price.replace('$', ''))
                if numeric_price <= price_threshold:
                    logging.info(f"Low price found: {price}")
                    message = f"Alert: Flight price dropped to {price}!"
                    send_email_alert(email, password, message)
                    break
            else:
                logging.info("No prices below the threshold were found.")

        except Exception as e:
            logging.error(f"An error occurred: {e}")
        finally:
            driver.quit()
    else:
        logging.error("WebDriver setup failed. Exiting.")

if __name__ == "__main__":
    main()
