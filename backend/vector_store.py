import logging
from langchain_chroma import Chroma
from config import CHROMA_PERSIST_DIR

logger = logging.getLogger(__name__)

# Global variables to hold vector stores
workout_vectorstore = None
nutrition_vectorstore = None
embeddings = None

def init_vector_stores():
    global workout_vectorstore, nutrition_vectorstore, embeddings
    
    logger.info("Initializing local ChromaDB vector stores...")
    
    from langchain_huggingface import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    workout_vectorstore = Chroma(
        collection_name="workouts",
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )
        
    nutrition_vectorstore = Chroma(
        collection_name="nutrition",
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )
    
    logger.info("Local ChromaDB vector stores are ready.")

def get_workout_retriever(k=5):
    if workout_vectorstore:
        return workout_vectorstore.as_retriever(search_kwargs={"k": k})
    return None

def get_nutrition_retriever(k=5):
    if nutrition_vectorstore:
        return nutrition_vectorstore.as_retriever(search_kwargs={"k": k})
    return None
