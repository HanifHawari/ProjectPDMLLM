"""
Router: /api/programs
"""
from fastapi import APIRouter, Query
from typing import Optional

from data_loader import ds, search_programs, get_program_detail
from models import APIResponse

router = APIRouter()


@router.get("")
async def list_programs(
    level: Optional[str] = Query(None, description="beginner | intermediate | advanced"),
    goal: Optional[str] = Query(None, description="muscle gain | weight loss | strength | endurance"),
    equipment: Optional[str] = Query(None, description="Full Gym | Garage Gym | Dumbbell Only"),
    max_weeks: Optional[int] = Query(None, description="Maksimal durasi program (minggu)"),
    q: Optional[str] = Query(None, description="Keyword search"),
    limit: int = Query(20, le=100),
):
    """Cari dan filter program latihan."""
    results = search_programs(
        level=level,
        goal=goal,
        equipment=equipment,
        max_weeks=max_weeks,
        query=q,
        limit=limit,
    )
    return APIResponse(success=True, data=results, total=len(results))


@router.get("/levels")
async def get_levels():
    """Daftar level yang tersedia."""
    if ds.programs is None or ds.programs.empty:
        return APIResponse(success=False, message="Dataset tidak tersedia")
    col = next((c for c in ds.programs.columns if c.lower() == "level"), None)
    if not col:
        return APIResponse(success=True, data=[])
    levels = ds.programs[col].dropna().unique().tolist()
    return APIResponse(success=True, data=sorted(levels))


@router.get("/goals")
async def get_goals():
    """Daftar goal yang tersedia."""
    if ds.programs is None or ds.programs.empty:
        return APIResponse(success=False, message="Dataset tidak tersedia")
    col = next((c for c in ds.programs.columns if c.lower() == "goal"), None)
    if not col:
        return APIResponse(success=True, data=[])
    goals = ds.programs[col].dropna().unique().tolist()
    return APIResponse(success=True, data=sorted(goals))


@router.get("/equipment")
async def get_equipment_types():
    """Daftar equipment yang tersedia."""
    if ds.programs is None or ds.programs.empty:
        return APIResponse(success=False, message="Dataset tidak tersedia")
    col = next((c for c in ds.programs.columns if "equipment" in c.lower()), None)
    if not col:
        return APIResponse(success=True, data=[])
    equip = ds.programs[col].dropna().unique().tolist()
    return APIResponse(success=True, data=sorted(equip))


@router.get("/detail")
async def get_program_detail_endpoint(
    title: str = Query(..., description="Judul program (partial match)"),
    week: Optional[int] = Query(None, description="Filter minggu tertentu"),
    day: Optional[int] = Query(None, description="Filter hari tertentu"),
):
    """
    Ambil detail latihan per program dari programs_detailed dataset.
    File ini besar (294MB), dimuat secara lazy saat pertama kali dipanggil.
    """
    results = get_program_detail(title=title, week=week, day=day)
    return APIResponse(
        success=True,
        data=results,
        total=len(results),
        message="programs_detail dimuat dari file 294MB" if results else "Program tidak ditemukan"
    )


@router.get("/stats")
async def get_program_stats():
    """Statistik ringkasan dari program library."""
    if ds.programs is None or ds.programs.empty:
        return APIResponse(success=False, message="Dataset tidak tersedia")

    df = ds.programs
    stats = {
        "total_programs": len(df),
    }

    for col_name, key in [("level", "by_level"), ("goal", "by_goal"), ("equipment", "by_equipment")]:
        col = next((c for c in df.columns if c.lower() == col_name), None)
        if col:
            stats[key] = df[col].value_counts().head(10).to_dict()

    return APIResponse(success=True, data=stats)
