from backend.app.core.config import settings
from backend.app.core.emails.base import EmailTemplate


class LoginOTPEmail(EmailTemplate):
    subject = "Your Login OTP Code"
    template_name = "login_otp.html"
    template_name_plain = "login_otp.txt"
    
    

async def send_login_otp_email(email: str, otp_code: str) -> None:
    context = {
        "otp:": otp_code,
        "expire_time":settings.OTP_EXPIRATION_MINUTES,
        "site_name": settings.SITE_NAME,
        
    }
    await LoginOTPEmail.send_email(email_to=email, context=context)