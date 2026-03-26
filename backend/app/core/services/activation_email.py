from backend.app.core.config import settings
from backend.app.core.emails.base import EmailTemplate


class ActivationEmail(EmailTemplate):
    subject = "Activate Your Account"
    template_name = "activation_email.html"
    template_name_plain = "activation_email.txt"


async def send_activation_email(email: str, activation_link: str) -> None:
    activation_url = (
        f"{settings.API_BASE_URL}{settings.API_V1_STR}/auth/activate/{{token}}"
    )
    context = {
        "activation_url": activation_url,
        "support_email": settings.SUPPORT_EMAIL,
        "expire_time": settings.ACTIVATION_TOKEN_EXPIRATION_MINUTES,
        "site_name": settings.SITE_NAME,
    }
    await ActivationEmail.send_email(email_to=email, context=context)
