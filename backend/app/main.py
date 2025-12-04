from fastapi import FastAPI

from .api.main import api_router
from .core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/docs",
    openapi_url=f"{settings.API_V1_STR}/openai.json",
)
app.include_router(api_router, prefix=settings.API_V1_STR)
