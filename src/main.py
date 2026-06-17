from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

from api.http.routers import routers
from config import settings
from libs.logger.custom_logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    # from src.infrastructure.db import close_engine

    # await close_engine()
    yield


app = FastAPI(title="Booking Service", version=settings.VERSION, lifespan=lifespan)

setup_logging()

from slowapi import Limiter, _rate_limit_exceeded_handler


# app.state.limiter = Limiter(key_func=lambda req: "global")
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.include_router(routers)
