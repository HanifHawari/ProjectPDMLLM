
"""
FitMind AI - Data Loader
Memuat semua dataset CSV ke memory saat startup.
Dataset besar (programs_detailed) dimuat secara lazy.

Optimasi:
  - LRU Cache pada semua fungsi pencarian (0ms untuk query berulang).
  - Vectorized Pandas operations (gantikan apply(lambda) yang lambat).
  - FutureWarning ditekan agar log terminal bersih.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from functools import lru_cache
import logging

# Opt-in ke perilaku Pandas masa depan agar tidak ada FutureWarning
pd.set_option("future.no_silent_downcasting", True)

from config import (
    WORKOUT_CSV, MASTER_NUTRITION_CSV, PROGRAMS_CSV,
    PROGRAMS_DETAIL_CSV, USER_PROFILES_CSV
)

logger = logging.getLogger(__name__)


# ==============================================================
# Dataset Store (singleton, dimuat sekali saat startup)
# ==============================================================
class DataStore:
    """Container untuk semua dataset yang sudah dimuat."""

    workout: pd.DataFrame = None
    master_nutrition: pd.DataFrame = None
    programs: pd.DataFrame = None
    user_profiles: pd.DataFrame = None

    # programs_detail dimuat lazy (file besar)
    _programs_detail_path: Path = PROGRAMS_DETAIL_CSV
    _programs_detail_loaded: bool = False
    programs_detail: pd.DataFrame = None


# Singleton instance
ds = DataStore()


# ==============================================================
# Loader Functions
# ==============================================================

def _safe_read_csv(path: Path, **kwargs) -> pd.DataFrame:
    """Baca CSV dengan error handling dan logging."""
    try:
        df = pd.read_csv(path, encoding="utf-8", low_memory=False, **kwargs)
        logger.info(f"✅ Loaded {path.name}: {len(df):,} rows, {len(df.columns)} cols")
        return df
    except FileNotFoundError:
        logger.error(f"❌ File tidak ditemukan: {path}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"❌ Error membaca {path.name}: {e}")
        return pd.DataFrame()


def load_all_datasets():
    """
    Muat semua dataset utama ke DataStore.
    Dipanggil saat FastAPI startup.
    Programs detail TIDAK dimuat di sini (terlalu besar, lazy-loaded).
    """
    logger.info("🔄 Memuat semua dataset...")

    # 1. Workout library (52 baris - ringan)
    ds.workout = _safe_read_csv(WORKOUT_CSV)
    if not ds.workout.empty:
        ds.workout.columns = ds.workout.columns.str.strip()
        # Pre-lower semua string agar pencarian lebih cepat
        _str_cols_workout = ds.workout.select_dtypes(include="object").columns
        for col in _str_cols_workout:
            ds.workout[f"_{col}_lower"] = ds.workout[col].astype(str).str.lower().fillna("")

    # 2. Master Nutrition (~35k baris, gabungan USDA, Healthy Foods, dan Allergens)
    ds.master_nutrition = _safe_read_csv(MASTER_NUTRITION_CSV)
    if not ds.master_nutrition.empty:
        # Pre-lower nama makanan untuk pencarian cepat
        if "food_name" in ds.master_nutrition.columns:
            ds.master_nutrition["_food_name_lower"] = (
                ds.master_nutrition["food_name"].astype(str).str.lower().fillna("")
            )

    # 3. Program summary (~10k baris)
    ds.programs = _safe_read_csv(PROGRAMS_CSV)
    if not ds.programs.empty:
        ds.programs.columns = ds.programs.columns.str.strip()
        # Pre-build kolom numerik weeks agar filter max_weeks instan
        if "program_length" in ds.programs.columns:
            ds.programs["_weeks_num"] = pd.to_numeric(
                ds.programs["program_length"].astype(str).str.extract(r"(\d+)")[0],
                errors="coerce"
            )

    # 4. User profiles (975 baris)
    ds.user_profiles = _safe_read_csv(USER_PROFILES_CSV)
    if not ds.user_profiles.empty:
        if "BMI" not in ds.user_profiles.columns:
            w_col = next((c for c in ds.user_profiles.columns if "Weight" in c), None)
            h_col = next((c for c in ds.user_profiles.columns if "Height" in c), None)
            if w_col and h_col:
                ds.user_profiles["BMI"] = (
                    ds.user_profiles[w_col] / (ds.user_profiles[h_col] ** 2)
                ).round(2)

    logger.info("✅ Semua dataset berhasil dimuat!")


def load_programs_detail():
    """
    Muat programs_detail secara LAZY — hanya saat pertama kali diperlukan.
    """
    if ds._programs_detail_loaded:
        return ds.programs_detail

    logger.info("🔄 Memuat programs_detail (file besar)...")
    try:
        ds.programs_detail = pd.read_csv(
            PROGRAMS_DETAIL_CSV,
            encoding="utf-8",
            low_memory=False
        )
        ds._programs_detail_loaded = True
        logger.info(f"✅ Programs detail dimuat: {len(ds.programs_detail):,} baris")
    except Exception as e:
        logger.error(f"❌ Gagal muat programs detail: {e}")
        ds.programs_detail = pd.DataFrame()
        ds._programs_detail_loaded = True

    return ds.programs_detail


# ==============================================================
# Query Helpers
# Menggunakan @lru_cache agar kueri yang sama hanya dihitung sekali.
# Semua parameter harus hashable (str, float, bool, int).
# ==============================================================

@lru_cache(maxsize=256)
def search_workout(body_part: str = None, muscle: str = None) -> list[dict]:
    """
    Cari workout berdasarkan body part atau muscle.
    LRU-cached: kueri berulang (misal: 'chest', 'dada') direspons 0ms.
    """
    if ds.workout is None or ds.workout.empty:
        return []

    df = ds.workout

    if body_part:
        bp = body_part.lower()
        # Cari di kolom _*_lower yang sudah di-precompute saat startup
        lower_cols = [c for c in df.columns if c.startswith("_") and c.endswith("_lower")]
        if lower_cols:
            mask = df[lower_cols].apply(lambda col: col.str.contains(bp, na=False)).any(axis=1)
        else:
            # Fallback vectorized (tidak pakai lambda per-row)
            mask = df.apply(lambda r: bp in str(r).lower(), axis=1)
        df = df[mask]

    if muscle:
        mu = muscle.lower()
        lower_cols = [c for c in df.columns if c.startswith("_") and c.endswith("_lower")]
        if lower_cols:
            mask = df[lower_cols].apply(lambda col: col.str.contains(mu, na=False)).any(axis=1)
        else:
            mask = df.apply(lambda r: mu in str(r).lower(), axis=1)
        df = df[mask]

    # Return hanya kolom asli (bukan _*_lower)
    original_cols = [c for c in df.columns if not c.startswith("_")]
    return df[original_cols].fillna("").to_dict(orient="records")


@lru_cache(maxsize=512)
def search_foods(
    query: str = None,
    max_calories: float = None,
    min_health_score: float = None,
    food_type: str = None,
    limit: int = 20
) -> list[dict]:
    """
    Cari makanan dari master nutrition database.
    LRU-cached: pencarian 'chicken breast', 'apple', dll direspons instan.
    """
    if ds.master_nutrition is None or ds.master_nutrition.empty:
        return []

    df = ds.master_nutrition

    if query:
        q = query.lower()
        # Gunakan kolom _food_name_lower yang sudah di-precompute
        if "_food_name_lower" in df.columns:
            df = df[df["_food_name_lower"].str.contains(q, na=False, regex=False)]
        else:
            df = df[df["food_name"].str.contains(q, case=False, na=False)]

    if max_calories is not None and "calories" in df.columns:
        df = df[df["calories"] <= max_calories]

    if min_health_score is not None and "health_score" in df.columns:
        df = df[df["health_score"] >= min_health_score]

    if food_type and "food_type" in df.columns:
        df = df[df["food_type"].str.contains(food_type, case=False, na=False)]

    # Return hanya kolom asli
    original_cols = [c for c in df.columns if not c.startswith("_")]
    return df[original_cols].head(limit).fillna("").to_dict(orient="records")


@lru_cache(maxsize=256)
def search_foods_allergen_free(
    query: str = None,
    exclude_gluten: bool = False,
    exclude_dairy: bool = False,
    exclude_nuts: bool = False,
    exclude_soy: bool = False,
    exclude_eggs: bool = False,
    exclude_fish: bool = False,
    limit: int = 20
) -> list[dict]:
    """
    Cari makanan bebas alergen dari master nutrition dataset.
    LRU-cached: kombinasi filter alergen yang sama direspons instan.
    """
    if ds.master_nutrition is None or ds.master_nutrition.empty:
        return []

    df = ds.master_nutrition

    # Vectorized boolean filter (jauh lebih cepat dari loop)
    filters = {
        "contains_gluten": exclude_gluten,
        "contains_dairy":  exclude_dairy,
        "contains_nuts":   exclude_nuts,
        "contains_soy":    exclude_soy,
        "contains_eggs":   exclude_eggs,
        "contains_fish":   exclude_fish,
    }
    for col, should_exclude in filters.items():
        if should_exclude and col in df.columns:
            df = df[df[col] != True]  # noqa: E712

    if query:
        q = query.lower()
        if "_food_name_lower" in df.columns:
            df = df[df["_food_name_lower"].str.contains(q, na=False, regex=False)]
        else:
            df = df[df["food_name"].str.contains(q, case=False, na=False)]

    original_cols = [c for c in df.columns if not c.startswith("_")]
    return df[original_cols].head(limit).fillna("").to_dict(orient="records")


@lru_cache(maxsize=256)
def search_programs(
    level: str = None,
    goal: str = None,
    equipment: str = None,
    max_weeks: int = None,
    query: str = None,
    limit: int = 20
) -> list[dict]:
    """
    Cari program latihan dari program_summary.
    LRU-cached: filter (beginner, weight_loss) yang sama direspons instan.
    """
    if ds.programs is None or ds.programs.empty:
        return []

    df = ds.programs

    # Semua filter berbasis kolom (vectorized, tidak ada lambda per-row)
    if level and "level" in df.columns:
        df = df[df["level"].str.contains(level, case=False, na=False)]

    if goal and "goal" in df.columns:
        df = df[df["goal"].str.contains(goal, case=False, na=False)]

    if equipment and "equipment" in df.columns:
        df = df[df["equipment"].str.contains(equipment, case=False, na=False)]

    if max_weeks and "_weeks_num" in df.columns:
        df = df[df["_weeks_num"] <= max_weeks]

    if query:
        q = query.lower()
        # Cari di kolom title dan description saja (bukan semua kolom)
        title_mask = df["title"].str.lower().str.contains(q, na=False, regex=False) \
            if "title" in df.columns else pd.Series(False, index=df.index)
        desc_mask = df["description"].str.lower().str.contains(q, na=False, regex=False) \
            if "description" in df.columns else pd.Series(False, index=df.index)
        df = df[title_mask | desc_mask]

    # Kembalikan hanya kolom asli (bukan _weeks_num)
    original_cols = [c for c in df.columns if not c.startswith("_")]
    return df[original_cols].head(limit).fillna("").to_dict(orient="records")


def get_program_detail(title: str, week: int = None, day: int = None) -> list[dict]:
    """Ambil detail latihan per program (dari programs_detail, lazy loaded)."""
    detail_df = load_programs_detail()
    if detail_df is None or detail_df.empty:
        return []

    df = detail_df[detail_df["title"].str.contains(title, case=False, na=False)]

    if week is not None:
        df = df[df["week"] == week]

    if day is not None:
        df = df[df["day"] == day]

    return df.head(100).fillna("").to_dict(orient="records")


def get_user_stats_summary() -> dict:
    """Statistik ringkasan dari dataset user profiles (untuk referensi LLM)."""
    if ds.user_profiles is None or ds.user_profiles.empty:
        return {}

    df = ds.user_profiles

    return {
        "total_members": len(df),
        "avg_bmi": round(df["BMI"].mean(), 2) if "BMI" in df.columns else None,
        "avg_calories_burned": round(
            df["Calories_Burned"].mean(), 1
        ) if "Calories_Burned" in df.columns else None,
        "avg_session_duration": round(
            df["Session_Duration (hours)"].mean(), 2
        ) if "Session_Duration (hours)" in df.columns else None,
        "workout_types": df["Workout_Type"].value_counts().to_dict()
            if "Workout_Type" in df.columns else {},
        "experience_distribution": df["Experience_Level"].value_counts().to_dict()
            if "Experience_Level" in df.columns else {},
    }


def invalidate_search_caches():
    """
    Bersihkan semua LRU cache (gunakan jika dataset di-reload ulang).
    Dipanggil saat hot-reload / admin trigger.
    """
    search_workout.cache_clear()
    search_foods.cache_clear()
    search_foods_allergen_free.cache_clear()
    search_programs.cache_clear()
    logger.info("🔄 LRU Search caches cleared.")
