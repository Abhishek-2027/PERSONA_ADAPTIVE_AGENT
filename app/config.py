import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    # App settings
    APP_NAME = os.getenv("APP_NAME", "Persona Adaptive Agent")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Ollama settings
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi")
    
    # Model settings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    
    # Paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    FAISS_INDEX_PATH = Path(os.getenv("FAISS_INDEX_PATH", BASE_DIR / "vector_store" / "index.faiss"))
    KB_DOCUMENTS_PATH = Path(os.getenv("KB_DOCUMENTS_PATH", BASE_DIR / "kb"))
    
    # Escalation settings
    ESCALATION_CONFIDENCE_THRESHOLD = float(os.getenv("ESCALATION_CONFIDENCE_THRESHOLD", 0.5))
    MAX_HISTORY_LENGTH = int(os.getenv("MAX_HISTORY_LENGTH", 5))
    
    # Create necessary directories
    FAISS_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    KB_DOCUMENTS_PATH.mkdir(parents=True, exist_ok=True)

# Global config instance
config = Config()