import os
import logging
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# Constants
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

# Global variables to hold vector stores
workout_vectorstore = None
nutrition_vectorstore = None
embeddings = None

def init_vector_stores():
    global workout_vectorstore, nutrition_vectorstore, embeddings
    
    # Import ds here to avoid circular imports if data_loader imports this
    from data_loader import ds
    
    logger.info("🔄 Initializing Vector Stores (ChromaDB)...")
    
    # Initialize embeddings (CPU friendly)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Initialize Workout Vector Store
    workout_vectorstore = Chroma(
        collection_name="workouts",
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )
    
    # Check if we need to ingest workouts
    if workout_vectorstore._collection.count() == 0 and ds.workout is not None:
        logger.info("Ingesting workouts into ChromaDB...")
        docs = []
        for _, row in ds.workout.iterrows():
            content = f"Exercise: {row.get('Title', '')}. Body Part: {row.get('BodyPart', '')}. Target Muscle: {row.get('TargetMuscle', '')}. Type: {row.get('Type', '')}. Equipment: {row.get('Equipment', '')}. Level: {row.get('Level', '')}. Description: {row.get('Desc', '')}"
            metadata = row.fillna("").to_dict()
            clean_metadata = {k: str(v) for k, v in metadata.items() if not k.startswith("_")}
            docs.append(Document(page_content=content, metadata=clean_metadata))
        if docs:
            workout_vectorstore.add_documents(docs)
            logger.info(f"✅ Ingested {len(docs)} workouts.")
        
    # Initialize Nutrition Vector Store
    nutrition_vectorstore = Chroma(
        collection_name="nutrition",
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )
    
    # Check if we need to ingest nutrition (limit to 1000 to save time for this demo, or ingest all)
    if nutrition_vectorstore._collection.count() == 0 and ds.healthy_foods is not None:
        logger.info("Ingesting healthy foods into ChromaDB...")
        docs = []
        # Taking top 1000 to prevent startup hanging for too long on standard laptops
        df_to_ingest = ds.healthy_foods.head(1000)
        for _, row in df_to_ingest.iterrows():
            food_name = row.get('food_name', '')
            content = f"Food: {food_name}. Calories: {row.get('calories', '')} kcal. Protein: {row.get('protein_g', '')}g. Carbs: {row.get('carbs_g', '')}g. Fat: {row.get('fat_g', '')}g. Health Score: {row.get('health_score', '')}"
            metadata = row.fillna("").to_dict()
            clean_metadata = {k: str(v) for k, v in metadata.items() if not k.startswith("_")}
            docs.append(Document(page_content=content, metadata=clean_metadata))
        if docs:
            nutrition_vectorstore.add_documents(docs)
            logger.info(f"✅ Ingested {len(docs)} foods.")

def get_workout_retriever(k=5):
    if workout_vectorstore:
        return workout_vectorstore.as_retriever(search_kwargs={"k": k})
    return None

def get_nutrition_retriever(k=5):
    if nutrition_vectorstore:
        return nutrition_vectorstore.as_retriever(search_kwargs={"k": k})
    return None
