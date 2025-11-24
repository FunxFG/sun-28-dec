import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_SECURITY = os.getenv("MAIL_SECURITY", "starttls")
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_FROM = os.getenv("MAIL_FROM", MAIL_USERNAME)
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Roadworks AI")
PASSWORD_RESET_URL = os.getenv("PASSWORD_RESET_URL", "http://127.0.0.1:3000/reset-password")
PASSWORD_RESET_EXPIRE_MINUTES = int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", "30"))


def send_password_reset_email(recipient_email: str, reset_token: str, company_name: Optional[str] = None) -> bool:
    """Send a password reset email via Gmail SMTP.

    This function uses environment variables for all credentials and URLs.
    """
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        # Email not configured; pretend success so UI flow still works
        print("[email_utils] MAIL_USERNAME or MAIL_PASSWORD not set; skipping actual send.")
        return True

    reset_url = f"{PASSWORD_RESET_URL}?token={reset_token}"

    display_name = company_name or "RoadworksAI User"

    subject = "RoadworksAI Password Reset Request"

    text_body = (
        f"Hi {display_name},\n\n"
        f"We received a request to reset your password for RoadworksAI.\n"
        f"You can reset your password by visiting the link below:\n\n"
        f"{reset_url}\n\n"
        f"This link will expire in {PASSWORD_RESET_EXPIRE_MINUTES} minutes.\n"
        f"If you did not request this, you can safely ignore this email.\n\n"
        f"Regards,\nRoadworksAI"
    )

    html_body = f"""
    <html>
      <body style='font-family: Arial, sans-serif; line-height: 1.5;'>
        <h2>Password reset request</h2>
        <p>Hi {display_name},</p>
        <p>We received a request to reset your password for <strong>RoadworksAI</strong>.</p>
        <p>
          Click the button below to set a new password (or copy the link if the button doesn't work):
        </p>
        <p>
          <a href="{reset_url}" style="background:#2563eb;color:#fff;padding:10px 18px;text-decoration:none;border-radius:4px;">
            Reset password
          </a>
        </p>
        <p style="word-break: break-all; font-size: 12px; color: #555;">
          {reset_url}
        </p>
        <p style="font-size: 12px; color: #666;">
          This link will expire in {PASSWORD_RESET_EXPIRE_MINUTES} minutes. If you did not request a password reset,
          you can safely ignore this email.
        </p>
      </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{MAIL_FROM_NAME} <{MAIL_FROM}>"
    msg["To"] = recipient_email

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        if MAIL_SECURITY == "starttls":
            server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)

        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_FROM, [recipient_email], msg.as_string())
        server.quit()
        print(f"[email_utils] Sent password reset email to {recipient_email}")
        return True
    except Exception as exc:  # pragma: no cover - log but don't crash
        print(f"[email_utils] Failed to send password reset email: {exc}")
        return False
