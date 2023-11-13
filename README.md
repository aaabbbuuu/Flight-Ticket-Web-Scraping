# Flight-Ticket-Web-Scraping

# Overview

This repository contains a Python script for web scraping flight ticket prices. It is designed for flexibility and requires some code changes in order to work. The script includes configurable parameters and an email alert feature for price drops.

# Contents
- README.md: This file, providing an overview and instructions.
- flights.py: The main Python script for scraping flight prices and sending email alerts.
- config.ini: Configuration file to set parameters like dates, price threshold, and email credentials.

# Features

- Configurable Parameters: Easily adjust flight dates, destinations, and price thresholds in the config.ini file.
- Robust Web Scraping: Uses Selenium WebDriver for dynamic web scraping.
- Error Handling and Logging: Improved error handling and logging for better debugging and reliability.
- Email Alerts: Sends notifications when flight prices fall below a set threshold.

# Usage

- Setup: Install Python, Selenium, and other dependencies.
- Configuration: Edit config.ini with your desired parameters, as well as code changes for flights.py.
- Execution: Run flights.py to start scraping. Email alerts are sent if conditions are met.

# Getting Started

Clone the repository
git clone https://github.com/aaabbbuuu/Flight-Ticket-Web-Scraping.git
To get started with this project, clone the repository and install the necessary dependencies. Ensure you have Python and Selenium WebDriver installed on your system.

Navigate to the repository directory
cd Flight-Ticket-Web-Scraping

Install dependencies
pip install selenium

Run the script
python flights.py

# License

This project is open-sourced under the MIT License.

# Contact

For any queries or suggestions, feel free to open an issue in the repository or contact me directly abu.t.hassan@gmail.com.
