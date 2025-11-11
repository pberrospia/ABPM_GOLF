from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import auth, reports
from app.core.config import settings
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(auth.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
