from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.http.routers import routers
from config import settings
from infrastructure.postgres.db import close_engine
from libs.logger.custom_logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_engine()


app = FastAPI(title="Booking Service", version=settings.VERSION, lifespan=lifespan)

setup_logging()

app.include_router(routers)
