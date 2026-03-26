import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.app.auth.models import User
from backend.app.auth.shema import AccountStatusSchema, UserCreateSchema
from backend.app.auth.utils import (
    generate_activation_token,
    generate_otp,
    generate_password_hash,
    generate_username,
    verify_password,
)
from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.core.services.activation_email import send_activation_email

logger = get_logger()


class UserAuthService:
    async def get_user_by_email(
        self, email: str, db: AsyncSession, include_inactive: bool = False
    ) -> User | None:
        query = select(User).where(User.email == email)
        if not include_inactive:
            query = query.where(User.is_active)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_user_by_id_no(
        self, id_no: uuid.UUID, db: AsyncSession, include_inactive: bool = False
    ) -> User | None:
        query = select(User).where(User.id_no == id_no)
        if not include_inactive:
            query = query.where(User.is_active)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_user_by_id(
        self, user_id: uuid.UUID, db: AsyncSession, include_inactive: bool = False
    ) -> User | None:
        query = select(User).where(User.id == user_id)
        if not include_inactive:
            query = query.where(User.is_active)
        result = await db.execute(query)
        return result.scalars().first()

    async def check_user_email_exists(self, email: str, db: AsyncSession) -> bool:
        query = await self.get_user_by_email(email=email, db=db)
        return bool(query)

    async def check_user_id_no_exists(self, id_no: uuid.UUID, db: AsyncSession) -> bool:
        query = await self.get_user_by_id_no(id_no=id_no, db=db)
        return bool(query)

    async def verify_user_password(
        self, plain_password: str, hashed_password: str
    ) -> bool:
        return verify_password(plain_password, hashed_password)

    async def reset_user_state(
        self,
        user: User,
        db: AsyncSession,
        *,
        clear_otp: bool = True,
        log_action: bool = True,
    ) -> None:
        previous_state = user.account_status
        user.failed_login_attempts = 0
        user.last_failed_login = None
        if clear_otp:
            user.otp = ""
            user.otp_expiry_time = None
        if user.account_status == AccountStatusSchema.LOCKED:
            user.account_status = AccountStatusSchema.ACTIVE
        await db.commit()
        await db.refresh(user)

        if log_action and previous_state != user.account_status:
            logger.info(
                f"User {user.email} account status reset from {previous_state} to {user.account_status}"
            )

    async def validate_user_status(self, user: User) -> None:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive. Please activate your account to proceed.",
            )

        if user.account_status == AccountStatusSchema.LOCKED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is locked due to multiple failed login attempts. Please try again later.",
            )

        if user.account_status == AccountStatusSchema.INACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive. Please activate your account to proceed.",
            )

    async def generate_and_save_otp(self, user: User, db: AsyncSession) -> tuple[bool, str]:  # type: ignore
        try:

            otp = generate_otp()
            user.otp = otp
            user.otp_expiry_time = datetime.now(timezone.utc) + timedelta(
                minutes=settings.OTP_EXPIRATION_MINUTES
            )
            await db.commit()
            await db.refresh(user)
            return True, otp
            # TODO: add send_login_otp_email function to send the OTP to user's email

        except Exception as e:
            logger.error(f"Error generating OTP for user {user.email}: {str(e)}")

            user.otp = ""
            user.otp_expiry_time = None
            await db.commit()
            await db.refresh(user)

    async def create_user(self, user_data: UserCreateSchema, db: AsyncSession) -> User:
        user_data_dict = user_data.model_dump(
            exclude={"confirm_password", "username", "is_active", "account_status"}
        )

        password = user_data_dict.pop("password")
        new_user = User(
            username=generate_username(),
            hashed_password=generate_password_hash(password),
            is_active=False,
            account_status=AccountStatusSchema.PENDING,
            **user_data_dict,
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        activation_token = generate_activation_token(new_user.id)
        try:
            await send_activation_email(new_user.email, activation_token)
            logger.info(
                f"Activation email sent to {new_user.email} for user ID {new_user.id}"
            )
        except Exception as e:
            logger.error(
                f"Error sending activation email to {new_user.email}: {str(e)}"
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send activation email. Please try again later.",
            )
        return new_user

    async def activate_user_account(self, token: str, db: AsyncSession) -> User:
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            if payload.get("type") != "activation":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid activation token.",
                )
            user_id = uuid.UUID(payload.get("user_id"))
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid activation token.",
                )

            user = await self.get_user_by_id(
                user_id=user_id, db=db, include_inactive=True
            )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found.",
                )
            if user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Account is already activated",
                )
            await self.reset_user_state(
                user=user, db=db, clear_otp=True, log_action=False
            )
            user.is_active = True
            user.account_status = AccountStatusSchema.ACTIVE
            await db.commit()
            await db.refresh(user)
            return user

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Activation token has expired.",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid activation token.",
            )
