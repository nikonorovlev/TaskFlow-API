from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import stats, tasks
from app.core.config import get_settings
from app.db.database import create_db_and_tables

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION,
              description="REST API for task management", debug=settings.DEBUG, lifespan=lifespan)

@app.get("/", tags=["General"])
def root():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION}

@app.get("/health", tags=["General"])
def health():
    return {"status": "ok"}

app.include_router(tasks.router, prefix=settings.API_PREFIX)
app.include_router(stats.router, prefix=settings.API_PREFIX)
