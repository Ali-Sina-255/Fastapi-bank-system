from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.core.model_registry import load_models

logger = get_logger()

engine = create_async_engine(settings.DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session

        except Exception as e:
            logger.error(f"An error occurrd while getting the database session: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    try:
        load_models()
        logger.info("Models loaded successfully")

    except ImportError:
        logger.info("Models was not loaded successfully : {e}")
