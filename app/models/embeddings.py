from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
from app.utils.logger import logger
from app.config import config

class EmbeddingModel:
    """Singleton wrapper for SentenceTransformer embedding model"""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self._load_model()
    
    def _load_model(self):
        """Load the embedding model"""
        try:
            logger.info(f"Loading embedding model: {config.EMBEDDING_MODEL}")
            self._model = SentenceTransformer(config.EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            # Fallback to a smaller model
            logger.info("Falling back to all-MiniLM-L6-v2")
            self._model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def encode(self, text: Union[str, List[str]]) -> np.ndarray:
        """Encode text to embeddings"""
        if isinstance(text, str):
            text = [text]
        
        embeddings = self._model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embeddings
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension"""
        return self._model.get_sentence_embedding_dimension()

# Global instance
embedding_model = EmbeddingModel()