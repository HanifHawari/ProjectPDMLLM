import os
import sys
import logging
import shutil
from pathlib import Path

# Tambahkan direktori backend ke sys.path agar bisa import modul backend
backend_dir = Path(__file__).parent.parent.resolve()
sys.path.append(str(backend_dir))

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import pandas as pd
from config import CHROMA_PERSIST_DIR, GEMINI_API_KEY, WORKOUT_CSV, HEALTHY_FOODS_CSV

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Mulai proses ingestion ChromaDB...")
    
    try:
        df_workout = pd.read_csv(WORKOUT_CSV)
        df_healthy_foods = pd.read_csv(HEALTHY_FOODS_CSV)
    except Exception as e:
        logger.error(f"Gagal memuat dataset: {e}")
        return
        
    if df_workout.empty or df_healthy_foods.empty:
        logger.warning("Dataset kosong atau tidak ditemukan.")
        return

    from langchain_huggingface import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Ingestion Workouts
    logger.info("Ingesting workouts into ChromaDB...")
    workout_docs = []
    for _, row in df_workout.iterrows():
        # Kolom CSV: Body Part, Type of Muscle, Workout, Sets, Reps per Set
        content = f"Exercise: {row.get('Workout', '')}. Body Part: {row.get('Body Part', '')}. Target Muscle: {row.get('Type of Muscle', '')}. Sets: {row.get('Sets', '')}. Reps: {row.get('Reps per Set', '')}"
        metadata = row.fillna("").to_dict()
        clean_metadata = {k: str(v) for k, v in metadata.items() if not k.startswith("_")}
        workout_docs.append(Document(page_content=content, metadata=clean_metadata))
    
    if workout_docs:
        Chroma.from_documents(
            documents=workout_docs,
            embedding=embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
            collection_name="workouts"
        )
        logger.info(f"✅ Ingested {len(workout_docs)} workouts.")

    # Ingestion Nutrition
    logger.info("Ingesting healthy foods into ChromaDB...")
    nutrition_docs = []
    # Menggunakan 1000 seperti sebelumnya agar tidak menghabiskan kuota API Gemini terlalu cepat
    df_to_ingest = df_healthy_foods.head(1000)
    for _, row in df_to_ingest.iterrows():
        food_name = row.get('food_name', '')
        content = f"Food: {food_name}. Calories: {row.get('calories', '')} kcal. Protein: {row.get('protein_g', '')}g. Carbs: {row.get('carbs_g', '')}g. Fat: {row.get('fat_g', '')}g. Health Score: {row.get('health_score', '')}"
        metadata = row.fillna("").to_dict()
        clean_metadata = {k: str(v) for k, v in metadata.items() if not k.startswith("_")}
        nutrition_docs.append(Document(page_content=content, metadata=clean_metadata))
    
    if nutrition_docs:
        Chroma.from_documents(
            documents=nutrition_docs,
            embedding=embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
            collection_name="nutrition"
        )
        logger.info(f"✅ Ingested {len(nutrition_docs)} foods.")

    logger.info("🎉 Ingestion ChromaDB selesai!")

if __name__ == "__main__":
    main()
