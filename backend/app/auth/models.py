import uuid
from datetime import datetime, timezone

from pydantic import computed_field
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy import func, text
from sqlmodel import Column, Field

from backend.app.auth.shema import BaseUserSchema, RoleChoicesSchema


class User(BaseUserSchema, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True),
    )

    hashed_password: str

    failed_login_attempts: int = Field(default=0, sa_column=Column(pg.SMALLINT))

    last_failed_login: datetime | None = Field(
        default=None, sa_column=Column(pg.TIMESTAMP(timezone=True))
    )

    otp: str = Field(default="", sa_column=Column(pg.VARCHAR(6)))

    otp_expiry_time: datetime | None = Field(
        default=None, sa_column=Column(pg.TIMESTAMP(timezone=True))
    )


    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=func.now(),
        ),
    )

    @computed_field
    @property
    def full_name(self) -> str:
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(filter(None, parts)).title()

    def has_role(self, role: RoleChoicesSchema) -> bool:
        return self.role == role
