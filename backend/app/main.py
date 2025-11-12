from __future__ import annotations

from fastapi import FastAPI

from app.api import reports

app = FastAPI(title="ABPM Analyzer")
app.include_router(reports.router)


@app.get("/health", tags=["health"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
