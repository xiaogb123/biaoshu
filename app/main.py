"""FastAPI 入口。Day 1 只提供 /health 和 /docs。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1 import documents,jobs


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title=f"{settings.APP_NAME} API",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(documents.router)
app.include_router(jobs.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}
