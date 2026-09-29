"""Isi katalog nutrisi dan program dari CSV saat tabelnya masih kosong."""

import csv
import logging
import math
import re

from sqlalchemy import func, insert, select

from config import MASTER_NUTRITION_CSV, PROGRAMS_CSV
from database.db_engine import SessionLocal
from database.db_models import DBMasterNutrition, DBProgramSummary


logger = logging.getLogger(__name__)


def _number(value):
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def _nutrition_row(row):
    data = {"food_name": row["food_name"], "food_type": row.get("food_type"), "source": row.get("source")}
    for key in ("calories", "protein_g", "fat_g", "carbs_g", "fiber_g", "sugar_g", "sodium_mg", "health_score"):
        data[key] = _number(row.get(key))
    for key in ("contains_gluten", "contains_dairy", "contains_nuts", "contains_soy", "contains_eggs", "contains_fish"):
        data[key] = str(row.get(key, "")).strip().lower() in {"true", "1", "yes"}
    data["_food_name_lower"] = row["food_name"].lower()
    return data


def _program_row(row):
    length = row.get("program_length") or ""
    weeks = re.search(r"\d+(?:\.\d+)?", length)
    exercises = _number(row.get("total_exercises"))
    data = {key: row.get(key) for key in (
        "title", "description", "level", "goal", "equipment", "program_length",
        "time_per_workout", "created", "last_edit",
    )}
    data["total_exercises"] = int(exercises) if exercises is not None else None
    data["_weeks_num"] = int(float(weeks.group())) if weeks else None
    return data


def _seed_table(db_factory, model, path, convert):
    if not path.is_file():
        logger.warning("Katalog %s belum tersedia: %s", model.__tablename__, path)
        return 0

    with db_factory.begin() as db:
        if db.scalar(select(func.count()).select_from(model)):
            return 0

        total = 0
        batch = []
        with path.open(newline="", encoding="utf-8-sig") as source:
            for row in csv.DictReader(source):
                batch.append(convert(row))
                if len(batch) == 500:
                    db.execute(insert(model), batch)
                    total += len(batch)
                    batch.clear()
            if batch:
                db.execute(insert(model), batch)
                total += len(batch)

    logger.info("Katalog %s diisi: %d baris", model.__tablename__, total)
    return total


def seed_catalogs(db_factory=SessionLocal, nutrition_csv=MASTER_NUTRITION_CSV, programs_csv=PROGRAMS_CSV):
    """Impor dua katalog yang dipakai halaman Nutrition dan Workout Program."""
    return {
        "nutrition": _seed_table(db_factory, DBMasterNutrition, nutrition_csv, _nutrition_row),
        "programs": _seed_table(db_factory, DBProgramSummary, programs_csv, _program_row),
    }
