"""
FitMind AI - Database Engine & Session Manager
Mengelola koneksi SQLite (dev) / PostgreSQL (prod) dengan SQLAlchemy.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from config import DATABASE_URL

logger = logging.getLogger(__name__)

# ==============================================================
# Engine
# ==============================================================
# connect_args hanya diperlukan untuk SQLite
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=_connect_args,
    pool_pre_ping=True,       # deteksi koneksi yang sudah mati sebelum dipakai
    echo=False,               # set True untuk debug SQL queries
)

# Aktifkan Foreign Key enforcement pada SQLite (by default SQLite mematikannya)
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# ==============================================================
# Session Factory
# ==============================================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==============================================================
# Dependency Injection (untuk FastAPI)
# ==============================================================
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency untuk mendapatkan DB session per-request.
    Gunakan sebagai: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==============================================================
# Init DB (buat semua tabel jika belum ada)
# ==============================================================
def init_db():
    """Buat semua tabel sesuai model. Dipanggil saat startup."""
    from database.db_models import Base
    logger.info("Inisialisasi database — membuat tabel yang belum ada...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database siap.")
