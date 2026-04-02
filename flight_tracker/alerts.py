"""Email alert delivery via Gmail SMTP."""

import logging
import smtplib
from email.message import EmailMessage

from .config import EmailConfig, FlightScraperConfig
from .scraper import FLIGHT_SEARCH_URL

logger = logging.getLogger(__name__)


def send_email_alert(
    email_conf: EmailConfig,
    low_price: int,
    flight_conf: FlightScraperConfig,
) -> bool:
    """Send a price-alert email. Returns True on success."""
    subject = (
        f"✈️ Flight Alert: {flight_conf.departure_code} → "
        f"{flight_conf.arrival_code} for ${low_price}!"
    )
    body = (
        f"A flight from {flight_conf.departure_code} to "
        f"{flight_conf.arrival_code} is available for ${low_price}, "
        f"below your ${flight_conf.price_threshold} threshold.\n\n"
        f"Dates: {flight_conf.start_date:%Y-%m-%d} to "
        f"{flight_conf.end_date:%Y-%m-%d}\n\n"
        f"Verify and book: {FLIGHT_SEARCH_URL}"
    )

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = email_conf.sender_email
    msg["To"] = email_conf.recipient_email

    try:
        logger.info("Sending alert to %s…", email_conf.recipient_email)
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email_conf.sender_email, email_conf.sender_password)
            server.send_message(msg)
        logger.info("Email sent.")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error(
            "SMTP auth failed — check credentials or use a Gmail App Password."
        )
    except Exception as exc:
        logger.error("Failed to send email: %s", exc)

    return False
