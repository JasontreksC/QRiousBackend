from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import engine
from app.routers import charms, students
from app.schemas import HealthResponse

app = FastAPI(
    title="QRious Backend",
    description="Student & Charm matching API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(students.router, prefix="/api")
app.include_router(charms.router, prefix="/api")


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
    return {"message": "QRious Backend API", "docs": "/docs"}
