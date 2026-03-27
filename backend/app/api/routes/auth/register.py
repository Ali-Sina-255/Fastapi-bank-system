from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.app.api.services.user_auth import user_auth_service
from backend.app.auth.shema import UserCreateSchema, UserReadSchema
from backend.app.core.db import get_session
from backend.app.core.logging import get_logger

logger = get_logger()
router = APIRouter(prefix="/auth", tags=["auth"])

# ================= DB =================
db_dependency = Annotated[AsyncSession, Depends(get_session)]


@router.post(
    "/register", response_model=UserReadSchema, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreateSchema,
    db: db_dependency,
) -> UserReadSchema:
    try:
        # Check if email exists - Fixed parameter order
        existing_email = await user_auth_service.get_user_by_email(
            email=user_data.email, db=db
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "error",
                    "message": "Email already registered",
                    "action": "Please use a different email address",
                },
            )

     
        existing_id = await user_auth_service.check_user_id_no_exists(
            id_no=user_data.id_no, db=db  
        )
        if existing_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "error",
                    "message": "ID number already taken",
                    "action": "Please choose a different ID number",
                },
            )

      
        new_user = await user_auth_service.create_user(user_data=user_data, db=db)

        logger.info(f"User registered successfully: {new_user.email}")
        return new_user

    except HTTPException as http_ex:
        await db.rollback()
        raise http_ex
    except Exception as e:
        await db.rollback()
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "An error occurred while registering the user",
                "action": "Please try again later",
            },
        )
