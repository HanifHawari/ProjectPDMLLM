"""
FitMind AI Backend - Configuration
Membaca environment variables dari .env file
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env dari folder backend/
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

# ==============================================================
# Gemini API
# ==============================================================
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ==============================================================
# App
# ==============================================================
APP_ENV: str = os.getenv("APP_ENV", "development")
APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT: int = int(os.getenv("APP_PORT", "8000"))

# ==============================================================
# Dataset Paths (relatif dari backend/)
# ==============================================================
DATASET_BASE = Path(os.getenv("DATASET_BASE_PATH", "../dataset"))

WORKOUT_CSV       = DATASET_BASE / "gerakan" / "Workout.csv"
# Menggunakan Master Nutrition (Gabungan USDA, Healthy Foods, dan Allergens)
MASTER_NUTRITION_CSV = DATASET_BASE / "nutrisiAI" / "master_nutrition.csv"
# Healthy Foods Database untuk tab "Makanan Sehat"
HEALTHY_FOODS_CSV = DATASET_BASE / "nutrisiAI" / "healthy_foods_database.csv"
PROGRAMS_CSV      = DATASET_BASE / "program" / "program_summary.csv"
# Menggunakan versi cleaned dari program detail
PROGRAMS_DETAIL_CSV = DATASET_BASE / "program" / "cleaned_programs_detailed.csv"
USER_PROFILES_CSV = DATASET_BASE / "userprofil" / "gym_members_exercise_tracking.csv"

# ==============================================================
# ChromaDB
# ==============================================================
CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

# ==============================================================
# Database (SQLAlchemy)
# ==============================================================
# SQLite untuk development, ganti dengan PostgreSQL URL untuk production
# Contoh PostgreSQL: postgresql+psycopg2://user:password@localhost:5432/fitmind_db
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'fitmind.db'}"
)

# ==============================================================
# CORS
# ==============================================================
# Set ALLOWED_ORIGINS di Railway Variables, pisahkan dengan koma.
# Contoh: https://frontend-fitmind.up.railway.app,http://localhost:5173
# Jika tidak diset, default mengizinkan semua origin (aman untuk testing).
_origins_raw: str = os.getenv("ALLOWED_ORIGINS", "*")
if _origins_raw == "*":
    ALLOWED_ORIGINS: list[str] = ["*"]
else:
    ALLOWED_ORIGINS: list[str] = [o.strip() for o in _origins_raw.split(",")]

