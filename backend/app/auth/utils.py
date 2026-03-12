import random
import string

from argon2 import passwordHasher
from argon2.exception import VerifyMismatchError

from backend.app.core.config import settings

_ph = passwordHasher()


def generate_otp(length: int = 6) -> str:
    otp = "".join(random.choice(string.digits, k=length))
    return otp


def generate_password_hash(password: str) -> str:
    return _ph.hash(password)


def verify_password(password: str, hashed_password: str) -> str:
    try:
        return _ph.verify(hashed_password, password)
    except VerifyMismatchError:
        return False


def generate_username() -> str:
    bank_name = settings.SITE_NAME
    words = bank_name.split()
    prefix = "".join([word[0] for word in words]).upper()
    remainder_length = 12 - len(prefix) - 1
    random_string = "".join(
        random.choice(string.ascii_uppercase + settings.digits, k=remainder_length)
    )
    username = f"{prefix}-{random_string}"
    return username
