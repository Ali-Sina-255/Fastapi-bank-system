from enum import Enum

from fastapi import HTTPException, status
from pydantic import EmailStr, field_validator
from sqlmodel import Field, SQLModel
import uuid


class SecurityQuestionSchema(str, Enum):
    MOTHER_MAIDEN_NAME = "mother_maiden_name"
    CHILDHOOD_FRIEND = "childhood_friend"
    FAVORITE_COLOR = "favorite_color"
    BIRTH_CITY = "birth_city"

    @classmethod
    def get_description(cls, value: "SecurityQuestionSchema") -> str:
        description = {
            cls.MOTHER_MAIDEN_NAME: "What is the name of your mother ?",
            cls.CHILDHOOD_FRIEND: "what is the name of childhood friends ?",
            cls.FAVORITE_COLOR: "What is your favorite color ?",
            cls.BIRTH_CITY: "what is the name of your city you ware born in ?",
        }
        return description.get(value, "Unknown security question")


class AccountStatusSchema(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    LOCKED = "Locked"
    PENDING = "Pending"


class RoleChoicesSchema(str, Enum):
    CUSTOMER = "Customer"
    ACCOUNT_EXECUTIVE = "Account_executive"
    BRANCH_MANAGER = "Branch_manager"
    ADMIN = "Admin"
    SUPER_ADMIN = "Super_admin"
    TELLER = "Teller"


class BaseUserSchema(SQLModel):
    username: str | None = Field(default=None, max_length=12, unique=True)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    first_name: str = Field(max_length=255)
    middle_name: str | None = Field(max_length=30, default=None)
    last_name: str = Field(max_length=255)

    id_no: int = Field(unique=True, gt=0)
    is_active: bool = False
    is_superuser: bool = False
    security_question: SecurityQuestionSchema = Field(max_length=30)
    security_answer: str = Field(max_length=30)

    account_status: AccountStatusSchema = Field(default=AccountStatusSchema.INACTIVE)
    role: RoleChoicesSchema = Field(default=RoleChoicesSchema.CUSTOMER)


class UserCreateSchema(BaseUserSchema):
    password: str = Field(min_length=8, max_length=40)
    confirm_password: str = Field(min_length=8, max_length=40)

    @field_validator("confirm_password")
    def validate_confirm_password(cls, v, values):
        if "password" in values.data and v != values.data["password"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "error",
                    "message": "Password do not match",
                    "action": "Please ensure that the password you entered match",
                },
            )
        return v


class UserReadSchema(BaseUserSchema):
    id: uuid.UUID
    full_name: str

class EmailRequestSchema(SQLModel):
    email: EmailStr

class LoginRequestSchema(SQLModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=40)


class OTPVerifyRequestSchema(SQLModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6) 
