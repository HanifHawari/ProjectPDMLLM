"""
FitMind AI - FastAPI Main Application
Startup → load datasets → register routers → run
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import ValidationError

from config import APP_HOST, APP_PORT, ALLOWED_ORIGINS
from data_loader import load_all_datasets
from database.db_engine import init_db
from routers import chat, workout, nutrition, programs, dashboard, users

# ==============================================================
# Logging Setup
# ==============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


# ==============================================================
# Lifespan (startup & shutdown)
# ==============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inisialisasi database dan muat dataset saat server startup."""
    logger.info("FitMind AI Backend starting...")
    init_db()
    load_all_datasets()
    logger.info("Server siap menerima request!")
    yield
    logger.info("👋 FitMind AI Backend shutting down...")


# ==============================================================
# App Instance
# ==============================================================
app = FastAPI(
    title="FitMind AI API",
    description="Backend API untuk FitMind AI — Gym & Nutrition LLM Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================
# Routers
# ==============================================================
app.include_router(chat.router,      prefix="/api/chat",      tags=["Chat"])
app.include_router(users.router,     prefix="/api/users",     tags=["Users"])
app.include_router(workout.router,   prefix="/api/workout",   tags=["Workout"])
app.include_router(nutrition.router, prefix="/api/nutrition", tags=["Nutrition"])
app.include_router(programs.router,  prefix="/api/programs",  tags=["Programs"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


# ==============================================================
# Root & Health Check
# ==============================================================
@app.get("/", tags=["Health"])
async def root():
    return {
        "app": "FitMind AI",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    from data_loader import ds
    return {
        "status": "healthy",
        "datasets_loaded": {
            "workout": ds.workout is not None and not ds.workout.empty,
            "master_nutrition": ds.master_nutrition is not None and not ds.master_nutrition.empty,
            "programs": ds.programs is not None and not ds.programs.empty,
            "user_profiles": ds.user_profiles is not None and not ds.user_profiles.empty,
            "programs_detail_lazy_loaded": ds._programs_detail_loaded,
        },
        "dataset_sizes": {
            "workout_rows": len(ds.workout) if ds.workout is not None else 0,
            "master_nutrition_rows": len(ds.master_nutrition) if ds.master_nutrition is not None else 0,
            "programs_rows": len(ds.programs) if ds.programs is not None else 0,
            "user_profiles_rows": len(ds.user_profiles) if ds.user_profiles is not None else 0,
        }
    }


# ==============================================================
# Entry Point
# ==============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=True,
        log_level="info"
    )
