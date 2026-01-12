import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import streamlit as st
from loguru import logger


def send_notification(email: str, name: str, city: str, aurora_value: float) -> bool:
    """
    User-facing aurora alert email notification.
    """
    subject = f"🌌 Aurora Alert for {city}"
    text_body = f"""
    Hi {name} 🌌,

Good news! An aurora event may be visible near {city}.

"""
    html_body = f"""
<!DOCTYPE html>
<html>
<body style="background-color:#0b1020;color:#ffffff;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center">
        <table width="600" cellpadding="24" cellspacing="0"
               style="background:#12172b;border-radius:12px;">

          <tr>
            <td>
              <h2 style="color:#cbd5ff;margin-top:0;">
                Hi {name} 👋
              </h2>

              <h1 style="color:#7df9ff;">🌌 Aurora Alert</h1>

              <p style="font-size:16px;">
                Northern Lights may be visible near <strong>{city}</strong>
              </p>

              <p style="font-size:16px;">
                ✨ <strong>Aurora Intensity:</strong> {aurora_value}
              </p>

              <div style="background:#1b2140;border-radius:8px;padding:16px;margin-top:20px;">
                🌠 Tip: Look north, avoid city lights, and check cloud cover.
              </div>

              <p style="margin-top:30px;color:#9aa4ff;">
                Clear skies and happy chasing ✨<br/>
                — <strong>Aurora Pulse</strong>
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
    return send_email_notification(email, subject, html_body, text_body)


def send_sms_notification(phone_number, message):
    """
    Stub function: Replace with real SMS sending.
    """
    logger.info(f"SMS sent to {phone_number}: {message}")


def send_email_notification(to_email: str, subject: str, html_body: str, text_body: str) -> bool:
    """
    Send an HTML + plain text email using SMTP.
    Returns True on success, False on failure.
    """
    try:
        email_cfg = st.secrets["email"]

        msg = MIMEMultipart()
        msg["From"] = email_cfg["sender_email"]
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(email_cfg["smtp_server"], email_cfg["smtp_port"]) as server:
            server.starttls()
            server.login(email_cfg["sender_email"], email_cfg["app_password"])
            server.send_message(msg)
        logger.info(f"Email sent to {to_email} with subject '{subject}'")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False
