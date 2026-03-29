from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail

from backend.app.core.config import settings

TEMPLATES_DIR = Path(__file__).parent / "templates"

email_config = ConnectionConfig(
    MAIL_FROM=settings.EMAIL_FROM,
    MAIL_FROM_NAME=settings.EMAIL_FROM_NAME,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_USERNAME=settings.SMTP_USER or "",  # <-- never None
    MAIL_PASSWORD=settings.SMTP_PASSWORD or "",  # <-- never None
    MAIL_STARTTLS=settings.EMAIL_USE_TLS,
    MAIL_SSL_TLS=settings.EMAIL_USE_SSL,
    USE_CREDENTIALS=False,  # Mailpit doesn’t need creds
    VALIDATE_CERTS=False,
    TEMPLATE_FOLDER=TEMPLATES_DIR,
)

fast_mail = FastMail(email_config)
