"""
Router: /api/workout
"""
from fastapi import APIRouter, Query
from typing import Optional

from data_loader import ds, search_workout
from models import APIResponse

router = APIRouter()


@router.get("")
async def get_all_workouts():
    """Ambil semua data workout dari CSV."""
    if ds.workout is None or ds.workout.empty:
        return APIResponse(success=False, message="Dataset workout tidak tersedia")
    return APIResponse(
        success=True,
        data=ds.workout.fillna("").to_dict(orient="records"),
        total=len(ds.workout)
    )


@router.get("/search")
async def search_workouts(
    body_part: Optional[str] = Query(None, description="Contoh: Chest, Back, Legs"),
    muscle: Optional[str] = Query(None, description="Contoh: Upper Chest, Hamstring"),
):
    """Cari workout berdasarkan body_part atau muscle group."""
    results = search_workout(body_part=body_part, muscle=muscle)
    return APIResponse(success=True, data=results, total=len(results))


@router.get("/body-parts")
async def get_body_parts():
    """Daftar unique body parts yang tersedia."""
    if ds.workout is None or ds.workout.empty:
        return APIResponse(success=False, message="Dataset tidak tersedia")

    col = next((c for c in ds.workout.columns if "body" in c.lower() or "part" in c.lower()), None)
    if not col:
        return APIResponse(success=False, message="Kolom body part tidak ditemukan")

    parts = ds.workout[col].dropna().unique().tolist()
    return APIResponse(success=True, data=parts, total=len(parts))


@router.get("/muscles")
async def get_muscle_types():
    """Daftar unique muscle types yang tersedia."""
    if ds.workout is None or ds.workout.empty:
        return APIResponse(success=False, message="Dataset tidak tersedia")

    col = next((c for c in ds.workout.columns if "muscle" in c.lower()), None)
    if not col:
        return APIResponse(success=False, message="Kolom muscle tidak ditemukan")

    muscles = ds.workout[col].dropna().unique().tolist()
    return APIResponse(success=True, data=muscles, total=len(muscles))


@router.get("/generate-split")
async def generate_weekly_split(
    days: int = Query(3, ge=1, le=6, description="Hari latihan per minggu"),
    body_parts: Optional[str] = Query(None, description="Comma-separated: Chest,Back,Legs")
):
    """
    Generate weekly workout split berdasarkan jumlah hari.
    Logic: 1=Full Body, 2=Upper/Lower, 3=PPL, 4=Upper/Lower x2, 5-6=Body Part Split
    """
    if ds.workout is None or ds.workout.empty:
        return APIResponse(success=False, message="Dataset tidak tersedia")

    # Mapping days → split
    SPLITS = {
        1: {"Full Body": None},
        2: {"Upper": ["Chest", "Back", "Shoulders", "Arms"],
            "Lower": ["Legs", "Abs"]},
        3: {"Push": ["Chest", "Shoulders"],
            "Pull": ["Back", "Arms"],
            "Legs": ["Legs", "Abs"]},
        4: {"Upper A": ["Chest", "Back"],
            "Lower A": ["Legs", "Abs"],
            "Upper B": ["Shoulders", "Arms"],
            "Lower B": ["Legs", "Abs"]},
        5: {"Chest": ["Chest"], "Back": ["Back"],
            "Legs": ["Legs"], "Shoulders": ["Shoulders"],
            "Arms + Abs": ["Arms", "Abs"]},
        6: {"Chest": ["Chest"], "Back": ["Back"], "Legs A": ["Legs"],
            "Shoulders": ["Shoulders"], "Arms": ["Arms"],
            "Legs B + Abs": ["Legs", "Abs"]},
    }

    split = SPLITS.get(days, SPLITS[3])

    result = {}
    for day_name, parts in split.items():
        if parts is None:
            # Full body
            all_exercises = search_workout()
            result[day_name] = all_exercises[:10]
        else:
            day_exercises = []
            for part in parts:
                exercises = search_workout(body_part=part)
                day_exercises.extend(exercises[:4])
            result[day_name] = day_exercises

    return APIResponse(success=True, data=result)
