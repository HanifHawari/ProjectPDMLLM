"""
Router: /api/dashboard
Statistik referensi dari dataset untuk dashboard & kalkulasi personal.
"""
import math
from fastapi import APIRouter, Query
from typing import Optional

from data_loader import get_user_stats_summary, ds
from models import APIResponse

router = APIRouter()


@router.get("/stats")
async def get_dataset_stats():
    """Statistik agregat dari gym members dataset (referensi benchmarking)."""
    stats = get_user_stats_summary()
    return APIResponse(success=True, data=stats)


@router.get("/dataset-overview")
async def get_dataset_overview():
    """Ringkasan semua dataset yang tersedia."""
    overview = {
        "workout_exercises": len(ds.workout) if ds.workout is not None else 0,
        "master_nutrition": len(ds.master_nutrition) if ds.master_nutrition is not None else 0,
        "programs": len(ds.programs) if ds.programs is not None else 0,
        "gym_members_profiles": len(ds.user_profiles) if ds.user_profiles is not None else 0,
    }
    return APIResponse(success=True, data=overview)


@router.get("/calculate-bmi")
async def calculate_bmi(
    weight_kg: float = Query(..., description="Berat badan (kg)"),
    height_m: float = Query(..., description="Tinggi badan (meter)"),
):
    """Hitung BMI dan kategori."""
    if height_m <= 0:
        return APIResponse(success=False, message="Tinggi badan tidak valid")

    bmi = round(weight_kg / (height_m ** 2), 2)

    if bmi < 18.5:
        category = "Underweight"
        color = "warning"
    elif bmi < 25:
        category = "Normal"
        color = "success"
    elif bmi < 30:
        category = "Overweight"
        color = "warning"
    else:
        category = "Obese"
        color = "danger"

    # Bandingkan dengan rata-rata dataset
    avg_bmi = None
    if ds.user_profiles is not None and not ds.user_profiles.empty and "BMI" in ds.user_profiles.columns:
        avg_bmi = round(ds.user_profiles["BMI"].mean(), 2)

    return APIResponse(success=True, data={
        "bmi": bmi,
        "category": category,
        "color": color,
        "weight_kg": weight_kg,
        "height_m": height_m,
        "dataset_avg_bmi": avg_bmi,
        "ideal_weight_range": {
            "min": round(18.5 * (height_m ** 2), 1),
            "max": round(24.9 * (height_m ** 2), 1),
        }
    })


@router.get("/estimate-calories")
async def estimate_calories_burned(
    age: int = Query(..., description="Usia"),
    weight_kg: float = Query(..., description="Berat badan (kg)"),
    avg_bpm: int = Query(..., description="Average heart rate selama sesi"),
    duration_hours: float = Query(..., description="Durasi sesi (jam)"),
    workout_type: str = Query("Strength", description="HIIT | Cardio | Strength | Yoga"),
):
    """
    Estimasi kalori terbakar berdasarkan formula Keytel et al.
    Menggunakan gender-neutral formula.
    """
    # Formula estimasi kalori (dari jurnal Keytel et al. 2005)
    # VO2 max proxy formula
    calories_per_min = (
        (-55.0969 + 0.6309 * avg_bpm + 0.1988 * weight_kg + 0.2017 * age) / 4.184
    )
    duration_minutes = duration_hours * 60
    base_calories = calories_per_min * duration_minutes

    # Intensifier per workout type
    MULTIPLIERS = {
        "HIIT": 1.15,
        "Cardio": 1.05,
        "Strength": 0.95,
        "Yoga": 0.80,
        "Mixed": 1.0,
    }
    multiplier = MULTIPLIERS.get(workout_type, 1.0)
    estimated_calories = round(max(0, base_calories * multiplier), 1)

    # Bandingkan dengan avg dataset
    avg_burned = None
    if ds.user_profiles is not None and not ds.user_profiles.empty:
        cal_col = next((c for c in ds.user_profiles.columns if "Calories" in c), None)
        if cal_col:
            avg_burned = round(ds.user_profiles[cal_col].mean(), 1)

    return APIResponse(success=True, data={
        "estimated_calories": estimated_calories,
        "duration_minutes": int(duration_minutes),
        "workout_type": workout_type,
        "multiplier_used": multiplier,
        "dataset_avg_calories_burned": avg_burned,
    })


@router.get("/bpm-analysis")
async def analyze_heart_rate(
    age: int = Query(..., description="Usia pengguna"),
    avg_bpm: int = Query(..., description="BPM rata-rata sesi"),
    max_bpm: int = Query(None, description="BPM maksimal sesi"),
    resting_bpm: int = Query(None, description="BPM istirahat"),
):
    """Analisis heart rate dan zona latihan."""
    max_hr_theory = 220 - age
    zones = {
        "Zone 1 (Recovery)": (0.50, 0.60),
        "Zone 2 (Fat Burn)": (0.60, 0.70),
        "Zone 3 (Cardio)": (0.70, 0.80),
        "Zone 4 (Anaerobic)": (0.80, 0.90),
        "Zone 5 (Max)": (0.90, 1.00),
    }

    # Tentukan zona dari avg_bpm
    current_zone = "Zone 1 (Recovery)"
    pct = avg_bpm / max_hr_theory
    for zone, (low, high) in zones.items():
        if low <= pct < high:
            current_zone = zone
            break

    zone_ranges = {
        zone: {
            "min_bpm": round(max_hr_theory * low),
            "max_bpm": round(max_hr_theory * high),
        }
        for zone, (low, high) in zones.items()
    }

    return APIResponse(success=True, data={
        "age": age,
        "theoretical_max_hr": max_hr_theory,
        "avg_bpm": avg_bpm,
        "avg_bpm_pct": round(pct * 100, 1),
        "current_zone": current_zone,
        "max_bpm": max_bpm,
        "resting_bpm": resting_bpm,
        "zones": zone_ranges,
    })
