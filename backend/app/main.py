import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from backend.app.api.main import api_router
from backend.app.core import logging
from backend.app.core.config import settings
from backend.app.core.db import engine, init_db
from backend.app.core.health import ServiceStatus, health_checker

logger = logging()


async def startup_health_check(timeout: float) -> bool:
    try:
        async with asyncio.timeout(timeout):
            retry_interval = [1, 2, 5, 10, 15]
            start_time = time.time()

            while True:
                is_healthy = await health_checker.wait_for_services()
                if is_healthy:
                    logger.info("Health check passed during startup.")
                    return True
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    logger.error(
                        "Health check failed during startup: Timeout exceeded."
                    )
                    return False
                wait_time = (
                    retry_interval[min(len(retry_interval) - 1, int(elapsed_time / 10))]
                    if retry_interval
                    else 15
                )
                logger.warning(
                    f"Health check failed during startup. Retrying in {wait_time} seconds..."
                )
                await asyncio.sleep(wait_time)
    except asyncio.TimeoutError:
        logger.error("Health check failed during startup: Timeout exceeded.")
        return False
    except Exception as e:
        logger.error(f"Health check failed during startup: {e}")
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting up application...")
        await init_db()
        logger.info("Database initialized successfully.")
        await health_checker.add_service("database", health_checker.check_database)
        await health_checker.add_service("redis", health_checker.check_redis)
        await health_checker.add_service("celery", health_checker.check_celery)
        if not await startup_health_check(timeout=60):
            raise RuntimeError("Startup health check failed.")
        logger.info("Startup health check initialized and healthy.")
        yield
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        await engine.dispose()
        await health_checker.cleanup()
        logger.error(f"Application startup failed: {e}")
        raise

    finally:
        logger.info("Shutting down application...")
        await engine.dispose()
        await health_checker.cleanup()
        logger.info("Application shutdown complete.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/docs",
    openapi_url=f"{settings.API_V1_STR}/openai.json",
    lifespan=lifespan,
)


@app.get("/health", response_model=dict)
async def health():
    try:
        health_status = await health_checker.check_all_services()
        if health_status["status"] == ServiceStatus.HEALTHY:
            status_code = status.HTTP_200_OK
            return health_status
        elif health_status["status"] == ServiceStatus.DEGRADED:
            status_code = status.HTTP_206_PARTIAL_CONTENT
            return health_status
        else:
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return JSONResponse(content=health_status, status_code=status_code)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={"status": ServiceStatus.UNHEALTHY, "details": {"error": str(e)}},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


app.include_router(api_router, prefix=settings.API_V1_STR)
