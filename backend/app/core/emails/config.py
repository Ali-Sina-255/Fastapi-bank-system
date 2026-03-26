from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail
from pydantic import SecretStr

from backend.app.core.config import settings

TEMPLATES_DIR = Path(__file__).parent / "templates"

email_config = ConnectionConfig(
    MAIL_FROM=settings.EMAIL_FROM,
    MAIL_FROM_NAME=settings.EMAIL_FROM_NAME,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=SecretStr(settings.SMTP_PASSWORD),
    MAIL_STARTTLS=True,  # ✅ Enable TLS
    MAIL_SSL_TLS=False,  # usually False when STARTTLS=True
    USE_CREDENTIALS=True,  # ✅ Enable auth
    VALIDATE_CERTS=True,  # ✅ Secure
    TEMPLATE_FOLDER=TEMPLATES_DIR,
)

fast_mail = FastMail(email_config)
