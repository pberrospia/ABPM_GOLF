from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import reports
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="ABPM Analyzer", lifespan=lifespan)
app.include_router(reports.router)


@app.get("/health", tags=["health"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
