import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from services.common.config import Config


def send_email(
    subject: str,
    body: str,
    to: str,
    is_html: bool = False,
):
    """
    Send email using SMTP config from Config
    :param subject: Email subject
    :param body: Email body
    :param to: Recipient email
    :param is_html: Is HTML content
    :return: None
    """
    sender = Config.SMTP_USER
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject

    logging.info(f"Sending email via SMTP host: {Config.SMTP_HOST}")

    if is_html:
        msg.attach(MIMEText(body, "html", "utf-8"))
    else:
        msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        if Config.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(Config.SMTP_HOST, Config.SMTP_PORT)
        else:
            server = smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT)
            server.starttls()
        server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
        server.sendmail(sender, [to], msg.as_string())
        server.quit()
        logging.info(f"Email sent successfully to {to}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        raise
