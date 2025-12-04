from fastapi import APIRouter

from app.core.logging import get_logger

logger = get_logger()
router = APIRouter(prefix="/home")


@router.get("/")
def home():
    logger.info("home page is access")
    logger.debug("home page is access")
    logger.error("home page is access")
    logger.warning("home page is access")
    logger.critical("home page is access")
    return {"message": "welcome to the nextGen banking system"}
