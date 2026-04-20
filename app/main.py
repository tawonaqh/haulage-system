import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import routes_auth, routes_drivers, routes_jobs, routes_trucks
from app.core.logging_config import configure_logging
from app.db.base import Base
from app.db.session import engine

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured")
    yield


app = FastAPI(
    title="Haulage Truck Management System",
    version="1.0.0",
    description="REST API for trucks, drivers, and delivery jobs.",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {
        "name": "Haulage Truck Management System",
        "version": "1.0.0",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
        "developed by": "tawona rwatida",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(routes_auth.router, prefix="/api/v1")
app.include_router(routes_trucks.router, prefix="/api/v1")
app.include_router(routes_drivers.router, prefix="/api/v1")
app.include_router(routes_jobs.router, prefix="/api/v1")
