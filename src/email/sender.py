"""
Multi-Provider Email Sender.
Supports Resend, Brevo, SendGrid, Gmail SMTP, and Console Dry-Run mode.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Dict, Any, Tuple
import requests

from src.utils.logger import get_logger

logger = get_logger("email_sender")


class EmailSender:
    def __init__(self, provider: Optional[str] = None):
        self.provider = (provider or os.environ.get("EMAIL_PROVIDER", "console")).lower()
        self.to_email = os.environ.get("EMAIL_TO") or os.environ.get("RECIPIENT_EMAIL")
        self.from_email = os.environ.get("EMAIL_FROM", "L&D Career Assistant <onboarding@resend.dev>")

    def send(
        self,
        subject: str,
        html_content: str,
        text_content: str,
        to_email: Optional[str] = None,
        dry_run: bool = False
    ) -> Tuple[bool, str]:
        """
        Sends email via configured provider or prints dry-run output.
        Returns (success: bool, message: str).
        """
        recipient = to_email or self.to_email

        if dry_run or self.provider in ["console", "dry_run", "test"]:
            logger.info("=" * 70)
            logger.info(f"DRY RUN EMAIL DISPATCH to: {recipient or 'Console'}")
            logger.info(f"Subject: {subject}")
            logger.info("=" * 70)
            print("\n--- PLAIN TEXT EMAIL PREVIEW ---\n")
            print(f"SUBJECT: {subject}\n")
            print(text_content)
            print("\n" + "=" * 70 + "\n")
            return True, "Dry-run execution completed. No email was sent."

        if not recipient:
            err = "Recipient email address is missing. Please set EMAIL_TO or RECIPIENT_EMAIL."
            logger.error(err)
            return False, err

        logger.info(f"Sending email via [{self.provider.upper()}] to {recipient}...")

        if self.provider == "resend":
            return self._send_resend(subject, html_content, text_content, recipient)
        elif self.provider == "brevo":
            return self._send_brevo(subject, html_content, text_content, recipient)
        elif self.provider == "sendgrid":
            return self._send_sendgrid(subject, html_content, text_content, recipient)
        elif self.provider in ["smtp", "gmail"]:
            return self._send_smtp(subject, html_content, text_content, recipient)
        else:
            err = f"Unknown email provider: {self.provider}. Available: resend, brevo, sendgrid, smtp, console"
            logger.error(err)
            return False, err

    def _send_resend(self, subject: str, html: str, text: str, recipient: str) -> Tuple[bool, str]:
        api_key = os.environ.get("RESEND_API_KEY")
        if not api_key:
            return False, "Missing RESEND_API_KEY in environment/secrets."

        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "from": self.from_email,
            "to": [recipient],
            "subject": subject,
            "html": html,
            "text": text
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=12)
            if resp.status_code in [200, 201]:
                logger.info("Email successfully delivered via Resend API.")
                return True, "Email delivered successfully via Resend."
            else:
                err = f"Resend API error {resp.status_code}: {resp.text}"
                logger.error(err)
                return False, err
        except Exception as e:
            err = f"Failed to send via Resend: {e}"
            logger.error(err)
            return False, err

    def _send_brevo(self, subject: str, html: str, text: str, recipient: str) -> Tuple[bool, str]:
        api_key = os.environ.get("BREVO_API_KEY")
        if not api_key:
            return False, "Missing BREVO_API_KEY in environment/secrets."

        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "sender": {"email": self.from_email.split("<")[-1].rstrip(">").strip() or "alerts@ldcareer.com", "name": "L&D Career Intelligence"},
            "to": [{"email": recipient}],
            "subject": subject,
            "htmlContent": html,
            "textContent": text
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=12)
            if resp.status_code in [200, 201]:
                logger.info("Email successfully delivered via Brevo API.")
                return True, "Email delivered successfully via Brevo."
            else:
                err = f"Brevo API error {resp.status_code}: {resp.text}"
                logger.error(err)
                return False, err
        except Exception as e:
            err = f"Failed to send via Brevo: {e}"
            logger.error(err)
            return False, err

    def _send_sendgrid(self, subject: str, html: str, text: str, recipient: str) -> Tuple[bool, str]:
        api_key = os.environ.get("SENDGRID_API_KEY")
        if not api_key:
            return False, "Missing SENDGRID_API_KEY in environment/secrets."

        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "personalizations": [{"to": [{"email": recipient}]}],
            "from": {"email": self.from_email.split("<")[-1].rstrip(">").strip() or "alerts@ldcareer.com"},
            "subject": subject,
            "content": [
                {"type": "text/plain", "value": text},
                {"type": "text/html", "value": html}
            ]
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=12)
            if resp.status_code in [200, 202]:
                logger.info("Email successfully delivered via SendGrid.")
                return True, "Email delivered successfully via SendGrid."
            else:
                err = f"SendGrid API error {resp.status_code}: {resp.text}"
                logger.error(err)
                return False, err
        except Exception as e:
            err = f"Failed to send via SendGrid: {e}"
            logger.error(err)
            return False, err

    def _send_smtp(self, subject: str, html: str, text: str, recipient: str) -> Tuple[bool, str]:
        host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
        port = int(os.environ.get("SMTP_PORT", 587))
        user = os.environ.get("SMTP_USER")
        password = os.environ.get("SMTP_PASSWORD")

        if not user or not password:
            return False, "Missing SMTP_USER or SMTP_PASSWORD credentials in environment/secrets."

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = recipient

        msg.attach(MIMEText(text, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))

        try:
            server = smtplib.SMTP(host, port, timeout=15)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(user, password)
            server.sendmail(self.from_email, [recipient], msg.as_string())
            server.quit()
            logger.info("Email successfully sent via SMTP.")
            return True, "Email sent successfully via SMTP."
        except Exception as e:
            err = f"SMTP dispatch failed: {e}"
            logger.error(err)
            return False, err
