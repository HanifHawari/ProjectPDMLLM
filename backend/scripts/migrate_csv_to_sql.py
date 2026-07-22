import os
import sys
import logging
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).parent.parent.resolve()
sys.path.append(str(backend_dir))

from database.db_engine import SessionLocal, init_db
from database.db_models import (
    DBWorkout, DBMasterNutrition, DBHealthyFood, 
    DBProgramSummary, DBProgramDetail
)
import pandas as pd
from config import WORKOUT_CSV, HEALTHY_FOODS_CSV, NUTRITION_CSV, PROGRAMS_CSV, PROGRAMS_DETAIL_CSV

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    logger.info("Mulai proses migrasi CSV ke SQL...")
    
    # 1. Pastikan tabel dibuat di Supabase
    logger.info("Membuat tabel baru jika belum ada di Supabase...")
    init_db()
    
    # 2. Buka sesi database
    db = SessionLocal()
    
    try:
        # Load Pandas data
        logger.info("Membaca file CSV...")
        df_workout = pd.read_csv(WORKOUT_CSV)
        df_healthy_foods = pd.read_csv(HEALTHY_FOODS_CSV)
        df_master_nutrition = pd.read_csv(NUTRITION_CSV)
        df_programs = pd.read_csv(PROGRAMS_CSV)
        
        # --- Workout ---
        if df_workout is not None and not df_workout.empty:
            count = db.query(DBWorkout).count()
            if count == 0:
                logger.info(f"Memigrasikan Workout ({len(df_workout)} baris)...")
                workouts = []
                for _, row in df_workout.iterrows():
                    body_part = str(row.get('Body Part', ''))
                    muscle = str(row.get('Type of Muscle', ''))
                    workouts.append(DBWorkout(
                        body_part=body_part,
                        type_of_muscle=muscle,
                        workout=str(row.get('Workout', '')),
                        sets=str(row.get('Sets', '')),
                        reps_per_set=str(row.get('Reps per Set', '')),
                        _body_part_lower=body_part.lower(),
                        _type_of_muscle_lower=muscle.lower()
                    ))
                db.add_all(workouts)
                db.commit()
                logger.info("✅ Migrasi Workout selesai.")
            else:
                logger.info(f"✅ Tabel Workout sudah ada ({count} baris). Melewati migrasi.")

        # --- Healthy Foods ---
        if df_healthy_foods is not None and not df_healthy_foods.empty:
            count = db.query(DBHealthyFood).count()
            if count == 0:
                logger.info(f"Memigrasikan Healthy Foods ({len(df_healthy_foods)} baris)...")
                foods = []
                for _, row in df_healthy_foods.iterrows():
                    name = str(row.get('food_name', ''))
                    
                    # Cek nan values
                    def _safe_float(val):
                        import math
                        if val is None or (isinstance(val, float) and math.isnan(val)):
                            return 0.0
                        try:
                            return float(val)
                        except:
                            return 0.0

                    foods.append(DBHealthyFood(
                        food_name=name,
                        food_type=str(row.get('food_type', '')),
                        calories=_safe_float(row.get('calories')),
                        protein_g=_safe_float(row.get('protein_g')),
                        fat_g=_safe_float(row.get('fat_g')),
                        carbs_g=_safe_float(row.get('carbs_g')),
                        fiber_g=_safe_float(row.get('fiber_g')),
                        sugar_g=_safe_float(row.get('sugar_g')),
                        sodium_mg=_safe_float(row.get('sodium_mg')),
                        health_score=_safe_float(row.get('health_score')),
                        _food_name_lower=name.lower()
                    ))
                db.add_all(foods)
                db.commit()
                logger.info("✅ Migrasi Healthy Foods selesai.")
            else:
                logger.info(f"✅ Tabel Healthy Foods sudah ada ({count} baris). Melewati migrasi.")

        # --- Master Nutrition ---
        if df_master_nutrition is not None and not df_master_nutrition.empty:
            count = db.query(DBMasterNutrition).count()
            if count == 0:
                logger.info(f"Memigrasikan Master Nutrition ({len(df_master_nutrition)} baris). Ini memakan waktu...")
                
                def _safe_float(val):
                    import math
                    if val is None or (isinstance(val, float) and math.isnan(val)):
                        return 0.0
                    try:
                        return float(val)
                    except:
                        return 0.0
                        
                chunk_size = 5000
                total = len(df_master_nutrition)
                for i in range(0, total, chunk_size):
                    chunk = df_master_nutrition.iloc[i:i+chunk_size]
                    nutrition_items = []
                    for _, row in chunk.iterrows():
                        name = str(row.get('food_name', ''))
                        nutrition_items.append(DBMasterNutrition(
                            food_name=name,
                            calories=_safe_float(row.get('calories')),
                            protein_g=_safe_float(row.get('protein_g')),
                            fat_g=_safe_float(row.get('fat_g')),
                            carbs_g=_safe_float(row.get('carbs_g')),
                            fiber_g=_safe_float(row.get('fiber_g')),
                            sugar_g=_safe_float(row.get('sugar_g')),
                            sodium_mg=_safe_float(row.get('sodium_mg')),
                            health_score=_safe_float(row.get('health_score')),
                            food_type=str(row.get('food_type', '')),
                            source=str(row.get('source', '')),
                            contains_gluten=bool(row.get('contains_gluten', False)),
                            contains_dairy=bool(row.get('contains_dairy', False)),
                            contains_nuts=bool(row.get('contains_nuts', False)),
                            contains_soy=bool(row.get('contains_soy', False)),
                            contains_eggs=bool(row.get('contains_eggs', False)),
                            contains_fish=bool(row.get('contains_fish', False)),
                            _food_name_lower=name.lower()
                        ))
                    db.add_all(nutrition_items)
                    db.commit()
                    logger.info(f"  > Dimasukkan {min(i+chunk_size, total)}/{total} baris...")
                logger.info("✅ Migrasi Master Nutrition selesai.")
            else:
                logger.info(f"✅ Tabel Master Nutrition sudah ada ({count} baris). Melewati migrasi.")

        # --- Program Summary ---
        if df_programs is not None and not df_programs.empty:
            count = db.query(DBProgramSummary).count()
            if count == 0:
                logger.info(f"Memigrasikan Program Summary ({len(df_programs)} baris)...")
                progs = []
                for _, row in df_programs.iterrows():
                    def _safe_int(val):
                        import math
                        if val is None or (isinstance(val, float) and math.isnan(val)):
                            return 0
                        try:
                            return int(val)
                        except:
                            return 0
                            
                    progs.append(DBProgramSummary(
                        title=str(row.get('title', '')),
                        description=str(row.get('description', '')),
                        level=str(row.get('level', '')),
                        goal=str(row.get('goal', '')),
                        equipment=str(row.get('equipment', '')),
                        program_length=str(row.get('program_length', '')),
                        time_per_workout=str(row.get('time_per_workout', '')),
                        total_exercises=_safe_int(row.get('total_exercises')),
                        created=str(row.get('created', '')),
                        last_edit=str(row.get('last_edit', '')),
                        _weeks_num=_safe_int(row.get('_weeks_num'))
                    ))
                db.add_all(progs)
                db.commit()
                logger.info("✅ Migrasi Program Summary selesai.")
            else:
                logger.info(f"✅ Tabel Program Summary sudah ada ({count} baris). Melewati migrasi.")

        # --- Program Detail ---
        prog_detail = pd.read_csv(PROGRAMS_DETAIL_CSV)
        if prog_detail is not None and not prog_detail.empty:
            count = db.query(DBProgramDetail).count()
            if count == 0:
                logger.info(f"Memigrasikan Program Detail ({len(prog_detail)} baris). Ini memakan waktu...")
                def _safe_int(val):
                    import math
                    if val is None or (isinstance(val, float) and math.isnan(val)):
                        return 0
                    try:
                        return int(val)
                    except:
                        return 0

                chunk_size = 5000
                total = len(prog_detail)
                for i in range(0, total, chunk_size):
                    chunk = prog_detail.iloc[i:i+chunk_size]
                    details = []
                    for _, row in chunk.iterrows():
                        details.append(DBProgramDetail(
                            title=str(row.get('title', '')),
                            description=str(row.get('description', '')),
                            level=str(row.get('level', '')),
                            goal=str(row.get('goal', '')),
                            equipment=str(row.get('equipment', '')),
                            program_length=str(row.get('program_length', '')),
                            time_per_workout=str(row.get('time_per_workout', '')),
                            week=_safe_int(row.get('week')),
                            day=_safe_int(row.get('day')),
                            number_of_exercises=_safe_int(row.get('number_of_exercises')),
                            exercise_name=str(row.get('exercise_name', '')),
                            sets=str(row.get('sets', '')),
                            reps=str(row.get('reps', '')),
                            intensity=str(row.get('intensity', ''))
                        ))
                    db.add_all(details)
                    db.commit()
                    logger.info(f"  > Dimasukkan {min(i+chunk_size, total)}/{total} baris...")
                logger.info("✅ Migrasi Program Detail selesai.")
            else:
                logger.info(f"✅ Tabel Program Detail sudah ada ({count} baris). Melewati migrasi.")
                
        logger.info("🎉 Seluruh data CSV telah dimigrasikan ke Supabase SQL!")

    except Exception as e:
        logger.error(f"❌ Terjadi kesalahan saat migrasi: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
