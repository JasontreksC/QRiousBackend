from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.admin import setup_admin
from app.database import engine
from app.errors import (
    AppError,
    app_error_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.routers import charms, stats, students, surveys
from app.schemas import HealthResponse

app = FastAPI(
    title="QRious Backend",
    description="Student survey & charm matching API",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(surveys.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(charms.router, prefix="/api")
app.include_router(students.router, prefix="/api")

setup_admin(app)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    return HealthResponse(status="ok" if db_status == "ok" else "degraded", database=db_status)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "QRious Backend API",
        "docs": "/docs",
        "admin": "/admin",
    }
