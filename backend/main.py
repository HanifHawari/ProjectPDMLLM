"""
FitMind AI - FastAPI Main Application
Startup → load datasets → register routers → run
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from config import APP_HOST, APP_PORT, ALLOWED_ORIGINS
from data_loader import load_all_datasets
from database.db_engine import init_db
from routers import chat, workout, nutrition, programs, dashboard, users

# Direktori hasil build frontend (frontend/dist → di-copy ke backend/dist saat build)
FRONTEND_DIST = Path(__file__).parent / "dist"

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
# Health Check (khusus API, tidak diganggu oleh SPA catch-all)
# ==============================================================
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
# Static Files (Frontend React — hanya aktif jika sudah di-build)
# ==============================================================
if FRONTEND_DIST.exists():
    logger.info(f"Serving frontend dari: {FRONTEND_DIST}")
    # Serve file statis (JS, CSS, gambar, video, dll)
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    # SPA catch-all: semua route yang bukan /api/* diarahkan ke index.html
    # Ini harus didaftarkan TERAKHIR agar tidak menimpa route API
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Cek apakah ada file statis langsung (favicon.ico, .mp4, .png, dll)
        file_path = FRONTEND_DIST / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        # Fallback ke index.html untuk SPA routing (React Router)
        return FileResponse(FRONTEND_DIST / "index.html")
else:
    logger.warning("Frontend dist/ tidak ditemukan. Jalankan: cd frontend && npm run build")

    @app.get("/", tags=["Health"])
    async def root():
        return {"app": "FitMind AI", "version": "1.0.0", "status": "running", "docs": "/docs"}


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
