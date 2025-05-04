# ✈️ Flight Price Tracker

This Python-based tool tracks flight prices between two airports over a given date range and sends you an email alert if the price drops below your configured threshold.

## 🚀 Features

- ✅ Headless flight price scraping using Selenium
- ✅ Dynamic ChromeDriver setup via `webdriver-manager`
- ✅ Secure credential management with `.env` file
- ✅ Email alerts for flight deals
- ✅ Configurable via `config.ini`

---

## ⚙️ Configuration

### 1. `config.ini`

Copy the example config and customize it:

```bash
cp config.ini.example config.ini
```

```ini
[FLIGHTS]
START_DATE=2025-12-20
END_DATE=2025-12-30
PRICE_THRESHOLD=600
DEPARTURE=LHE
ARRIVAL=ATL
```

### 2. `.env`

Store your email credentials securely:

```bash
cp .env.example .env
```

```env
FLIGHT_ALERT_EMAIL=youremail@gmail.com
FLIGHT_ALERT_PASSWORD=yourpassword
```

> ✅ Use **App Passwords** instead of your real password for Gmail if 2FA is enabled.

---

## 🧪 Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

Dependencies:
- `selenium`
- `webdriver-manager`
- `python-dotenv`

---

## 🛠️ How to Run

```bash
python flight_tracker.py
```

Make sure `config.ini` and `.env` are present in the same folder.

---

## 🧹 .gitignore

Recommended `.gitignore`:

```gitignore
.env
*.pyc
__pycache__/
chromedriver.log
```

---

## 📦 Optional Enhancements

- [ ] Add Dockerfile for containerized execution
- [ ] GitHub Action for scheduled price checks
- [ ] CLI mode with `argparse`
- [ ] CSV export of results

---

## 🤝 Contributing

Pull requests are welcome! Open issues or suggest features in the [Issues](https://github.com/yourname/flight-price-tracker/issues) tab.

---

## 📄 License

MIT © [Your Name](https://github.com/yourname)
