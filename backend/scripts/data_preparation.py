import pandas as pd
import os
from pathlib import Path
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATASET_DIR = BASE_DIR / "dataset"

def clean_programs_detailed():
    logger.info("Memulai pembersihan dataset programs_detailed...")
    input_path = DATASET_DIR / "program" / "programs_detailed_boostcamp_kaggle.csv"
    output_path = DATASET_DIR / "program" / "cleaned_programs_detailed.csv"
    
    if not input_path.exists():
        logger.warning(f"File {input_path} tidak ditemukan. Lewati.")
        return

    # Kolom yang benar-benar dibutuhkan oleh LLM/RAG
    usecols = [
        "title", "description", "level", "goal", "equipment",
        "program_length", "time_per_workout", "week", "day",
        "number_of_exercises", "exercise_name", "sets", "reps", "intensity"
    ]
    
    try:
        # Load dataset
        df = pd.read_csv(input_path, usecols=lambda c: c in usecols, low_memory=False)
        
        # Hapus baris yang kosong semua di kolom utama
        df.dropna(subset=["title", "exercise_name"], how="all", inplace=True)
        
        # Simpan
        df.to_csv(output_path, index=False)
        
        original_size = os.path.getsize(input_path) / (1024 * 1024)
        new_size = os.path.getsize(output_path) / (1024 * 1024)
        
        logger.info(f"✅ Berhasil membersihkan programs_detailed.")
        logger.info(f"Ukuran asli: {original_size:.2f} MB")
        logger.info(f"Ukuran baru: {new_size:.2f} MB")
    except Exception as e:
        logger.error(f"Gagal membersihkan programs_detailed: {e}")

def clean_and_merge_nutrition():
    logger.info("Memulai penggabungan dan pembersihan dataset Nutrisi...")
    usda_path = DATASET_DIR / "nutrisiAI" / "comprehensive_foods_usda.csv"
    healthy_path = DATASET_DIR / "nutrisiAI" / "healthy_foods_database.csv"
    allergens_path = DATASET_DIR / "nutrisiAI" / "foods_health_scores_allergens.csv"
    
    output_path = DATASET_DIR / "nutrisiAI" / "master_nutrition.csv"
    
    try:
        # 1. Bersihkan USDA
        df_usda = pd.read_csv(usda_path, low_memory=False) if usda_path.exists() else pd.DataFrame()
        if not df_usda.empty:
            # Ambil kolom esensial
            cols_usda = [
                'food_name', 'calories', 'protein_g', 'fat_g', 'carbs_g', 
                'fiber_g', 'sugar_g', 'sodium_mg', 'health_score', 'food_type'
            ]
            df_usda = df_usda[[c for c in cols_usda if c in df_usda.columns]].copy()
            df_usda['source'] = 'usda'

        # 2. Bersihkan Healthy Foods Database
        df_healthy = pd.read_csv(healthy_path, low_memory=False) if healthy_path.exists() else pd.DataFrame()
        if not df_healthy.empty:
            df_healthy['source'] = 'healthy_db'
            
        # Gabung (Concat) database makanan umum
        df_merged_foods = pd.concat([df_usda, df_healthy], ignore_index=True)
        df_merged_foods.drop_duplicates(subset=['food_name'], inplace=True)
        
        # 3. Proses Allergens (Health Scores Allergens)
        # File ini punya informasi alergen yang paling lengkap
        df_allergens = pd.read_csv(allergens_path, low_memory=False) if allergens_path.exists() else pd.DataFrame()
        if not df_allergens.empty:
            # Mapping boolean
            allergen_cols = [c for c in df_allergens.columns if c.startswith('contains_')]
            for col in allergen_cols:
                df_allergens[col] = df_allergens[col].map(
                    {True: True, False: False, 1: True, 0: False, 'true': True, 'false': False, 'yes': True, 'no': False}
                )
                
            cols_allergens = [
                'product_name', 'energy_kcal', 'proteins_100g', 'fat_100g', 'carbs_100g', 'sugars_100g',
                'contains_gluten', 'contains_dairy', 'contains_nuts', 'contains_soy', 'contains_eggs', 'contains_fish'
            ]
            df_allergens = df_allergens[[c for c in cols_allergens if c in df_allergens.columns]].copy()
            # Ganti nama kolom agar selaras
            df_allergens.rename(columns={
                'product_name': 'food_name',
                'energy_kcal': 'calories',
                'proteins_100g': 'protein_g',
                'fat_100g': 'fat_g',
                'carbs_100g': 'carbs_g',
                'sugars_100g': 'sugar_g'
            }, inplace=True)
            df_allergens['source'] = 'openfoodfacts'
            
            # Gabungkan dengan df_merged_foods
            df_master = pd.concat([df_merged_foods, df_allergens], ignore_index=True)
        else:
            df_master = df_merged_foods

        # Pembersihan Tipe Data Numerik
        numeric_cols = ["calories", "protein_g", "fat_g", "carbs_g", "fiber_g", "sugar_g", "sodium_mg", "health_score"]
        for col in numeric_cols:
            if col in df_master.columns:
                df_master[col] = pd.to_numeric(df_master[col], errors="coerce").fillna(0)

        # Isi NaN pada boolean dengan False
        for col in [c for c in df_master.columns if c.startswith('contains_')]:
            df_master[col] = df_master[col].fillna(False)

        # Simpan
        df_master.to_csv(output_path, index=False)
        
        logger.info(f"✅ Berhasil membuat master_nutrition.csv")
        logger.info(f"Jumlah total makanan: {len(df_master):,}")
        
    except Exception as e:
        logger.error(f"Gagal memproses dataset nutrisi: {e}")

if __name__ == "__main__":
    logger.info("=== FITMIND AI: DATA PREPARATION ===")
    # Buat direktori scripts jika belum ada
    Path(__file__).parent.mkdir(parents=True, exist_ok=True)
    
    clean_programs_detailed()
    clean_and_merge_nutrition()
    logger.info("=== SELESAI ===")
