from backend.app.core.config import settings
from backend.app.core.emails.base import EmailTemplate

class ActivationEmail(EmailTemplate):
    subject = "Activate Your Account"
    template_name = "activation_email.html"
    template_name_plain = "activation_email.txt"
    def __init__(self, user_email: str, activation_link: str):
        self.user_email = user_email
        self.activation_link = activation_link

    def get_context(self) -> dict:
        return {
            "activation_link": self.activation_link,
            "support_email": settings.SUPPORT_EMAIL,
        }

async def send_activation_email(user_email: str, activation_link: str) -> None:
    activation_url = f"{settings.API_BASE_URL}{settings.API_V1_STR}/auth/activate/{{token}}"
    context = {
        "activation_url": activation_url,
        "support_email": settings.SUPPORT_EMAIL,
        "expire_time": settings.ACTIVATION_TOKEN_EXPIRATION_MINUTES,
        "site_name": settings.SITE_NAME,
        
    }
    await ActivationEmail.send_email(email_to=email)
