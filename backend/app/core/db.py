import asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.core.model_registry import load_models

logger = get_logger()

engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=AsyncAdaptedQueuePool,
    pool_per_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = async_session()
    try:
        yield session
    except Exception as e:
        logger.error(f"Database session Error: {e}")
        if session:
            try:

                await session.rollback()
                logger.info("Database session rolled back successfully")
            except Exception as rollback_error:
                logger.error(f"Database session rollback Error: {rollback_error}")
        raise
    finally:
        if session:
            try:

                await session.close()
                logger.info("Database session closed successfully")
            except Exception as close_error:
                logger.error(f"Database session close Error: {close_error}")


async def init_db() -> None:
    try:
        load_models()
        logger.info("Models loaded successfully...")
        max_retries = 3
        retry_delay = 2
        for attempt in range(max_retries):
            try:
                async with engine.begin() as conn:
                    await conn.execute("SELECT 1")
                logger.info("Database connection established successfully")
                break
            except Exception:
                if attempt == max_retries - 1:
                    logger.error("Database connection failed after multiple attempts.")
                    raise
                logger.warning(
                    f"Database connection failed. Retrying in {retry_delay} seconds..."
                )

                await asyncio.sleep(retry_delay * (attempt + 1))

        logger.info("Models loaded successfully")

    except Exception as e:
        logger.error(f"Database initialization error: {e}")
