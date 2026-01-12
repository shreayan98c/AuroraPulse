import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import streamlit as st
from loguru import logger


def send_notification(email: str, city: str, aurora_value: float) -> bool:
    """
    User-facing aurora alert email notification.
    """
    subject = f"🌌 Aurora Alert for {city}"
    body = f"""
Hello 🌠,

Great news! An aurora event may be visible near **{city}**.

🌌 Aurora Intensity: {aurora_value}

Keep an eye on the sky and weather conditions for the best viewing experience!

— Aurora Pulse
"""
    return send_email_notification(email, subject, body)


def send_sms_notification(phone_number, message):
    """
    Stub function: Replace with real SMS sending.
    """
    logger.info(f"SMS sent to {phone_number}: {message}")


def send_email_notification(to_email: str, subject: str, body: str) -> bool:
    """
    Send an email using SMTP.
    Returns True on success, False on failure.
    """
    try:
        email_cfg = st.secrets["email"]

        msg = MIMEMultipart()
        msg["From"] = email_cfg["sender_email"]
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(email_cfg["smtp_server"], email_cfg["smtp_port"]) as server:
            server.starttls()
            server.login(email_cfg["sender_email"], email_cfg["app_password"])
            server.send_message(msg)
        logger.info(f"Email sent to {to_email} with subject '{subject}'")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False
