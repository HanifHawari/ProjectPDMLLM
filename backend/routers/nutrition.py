"""
Router: /api/nutrition
"""
from fastapi import APIRouter, Query
from typing import Optional

from data_loader import ds, search_foods, search_foods_allergen_free
from models import APIResponse, FoodSearchRequest

router = APIRouter()


@router.get("/search")
async def search_food(
    q: Optional[str] = Query(None, description="Nama makanan"),
    max_calories: Optional[float] = Query(None, description="Maksimal kalori per 100g"),
    min_health_score: Optional[float] = Query(None, description="Minimal health score (0-100)"),
    food_type: Optional[str] = Query(None, description="Tipe makanan"),
    no_gluten: bool = Query(False),
    no_dairy: bool = Query(False),
    no_nuts: bool = Query(False),
    no_soy: bool = Query(False),
    no_eggs: bool = Query(False),
    no_fish: bool = Query(False),
    limit: int = Query(20, le=100),
):
    """
    Cari makanan dengan filter nutrisi dan alergen.
    Menggabungkan data dari foods_usda + health_scores datasets.
    """
    # Jika ada filter alergen, gunakan health_scores dataset
    has_allergen_filter = any([no_gluten, no_dairy, no_nuts, no_soy, no_eggs, no_fish])

    if has_allergen_filter:
        results = search_foods_allergen_free(
            query=q,
            exclude_gluten=no_gluten,
            exclude_dairy=no_dairy,
            exclude_nuts=no_nuts,
            exclude_soy=no_soy,
            exclude_eggs=no_eggs,
            exclude_fish=no_fish,
            limit=limit,
        )
    else:
        results = search_foods(
            query=q,
            max_calories=max_calories,
            min_health_score=min_health_score,
            food_type=food_type,
            limit=limit,
        )

    return APIResponse(success=True, data=results, total=len(results))


@router.get("/healthy")
async def get_healthy_foods(
    food_type: Optional[str] = Query(None, description="Tipe: Vegetable, Fruit, Protein, dll"),
    min_score: float = Query(60, description="Minimal health score"),
    limit: int = Query(20, le=100),
):
    """Ambil makanan sehat dari healthy_foods_database."""
    if ds.healthy_foods is None or ds.healthy_foods.empty:
        return APIResponse(success=False, message="Dataset healthy foods tidak tersedia")

    df = ds.healthy_foods.copy()

    if "health_score" in df.columns:
        df = df[df["health_score"] >= min_score]

    if food_type and "food_type" in df.columns:
        df = df[df["food_type"].str.contains(food_type, case=False, na=False)]

    # Sort by health_score desc
    if "health_score" in df.columns:
        df = df.sort_values("health_score", ascending=False)

    results = df.head(limit).fillna("").to_dict(orient="records")
    return APIResponse(success=True, data=results, total=len(results))


@router.get("/food-types")
async def get_food_types():
    """Daftar unique food types dari healthy foods dataset."""
    if ds.healthy_foods is None or ds.healthy_foods.empty:
        return APIResponse(success=False, message="Dataset tidak tersedia")

    col = next((c for c in ds.healthy_foods.columns if "type" in c.lower()), None)
    if not col:
        return APIResponse(success=False, data=[], total=0)

    types = ds.healthy_foods[col].dropna().unique().tolist()
    return APIResponse(success=True, data=sorted(types), total=len(types))


@router.get("/meal-plan")
async def generate_meal_plan(
    target_calories: int = Query(2000, description="Target kalori harian"),
    diet_type: Optional[str] = Query(None, description="vegan | vegetarian | keto"),
    no_gluten: bool = Query(False),
    no_dairy: bool = Query(False),
):
    """
    Generate meal plan sederhana berdasarkan target kalori.
    Dibagi: Breakfast 25%, Lunch 35%, Dinner 30%, Snack 10%.
    """
    if ds.healthy_foods is None or ds.healthy_foods.empty:
        return APIResponse(success=False, message="Dataset tidak tersedia")

    df = ds.healthy_foods.copy()

    # Filter berdasarkan diet type
    if diet_type and "food_type" in df.columns:
        df = df[df["food_type"].str.contains(diet_type, case=False, na=False)]

    # Sort by health_score
    if "health_score" in df.columns:
        df = df.sort_values("health_score", ascending=False)

    df = df.fillna("")

    def pick_foods(target_cal: float, n: int = 3) -> list[dict]:
        """Pilih n makanan yang kalorinya mendekati target."""
        available = df[
            (df["calories"] > 0) & (df["calories"] <= target_cal * 1.5)
        ] if "calories" in df.columns else df
        return available.head(n).to_dict(orient="records")

    meal_plan = {
        "target_calories": target_calories,
        "breakdown": {
            "Breakfast": {
                "target_kcal": int(target_calories * 0.25),
                "foods": pick_foods(target_calories * 0.25 / 3),
            },
            "Lunch": {
                "target_kcal": int(target_calories * 0.35),
                "foods": pick_foods(target_calories * 0.35 / 3),
            },
            "Dinner": {
                "target_kcal": int(target_calories * 0.30),
                "foods": pick_foods(target_calories * 0.30 / 3),
            },
            "Snack": {
                "target_kcal": int(target_calories * 0.10),
                "foods": pick_foods(target_calories * 0.10 / 2, n=2),
            },
        }
    }

    return APIResponse(success=True, data=meal_plan)


@router.get("/nutriscore-stats")
async def get_nutriscore_distribution():
    """Distribusi Nutriscore grade dari dietary dataset."""
    if ds.dietary is None or ds.dietary.empty:
        return APIResponse(success=False, message="Dataset tidak tersedia")

    col = next((c for c in ds.dietary.columns if "nutriscore" in c.lower()), None)
    if not col:
        return APIResponse(success=False, data={}, message="Kolom nutriscore tidak ditemukan")

    dist = ds.dietary[col].value_counts().to_dict()
    return APIResponse(success=True, data=dist)
