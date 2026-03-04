import faiss
import numpy as np
import pickle
from typing import List, Dict, Any, Tuple
from pathlib import Path
from app.models.embeddings import embedding_model
from app.utils.helpers import load_kb_documents
from app.utils.logger import logger
from app.config import config

class VectorStore:
    """FAISS vector store for document retrieval"""
    
    def __init__(self):
        """Initialize vector store with paths from config"""
        self.kb_path = config.KB_DOCUMENTS_PATH
        self.index_path = config.FAISS_INDEX_PATH
        self.index = None
        self.documents = []
        self.document_embeddings = None
        self.dimension = embedding_model.dimension
        
        # Create index directory if it doesn't exist
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create index
        if self.index_path.exists():
            self.load()
        else:
            self.build_index()
    
    def build_index(self):
        """Build FAISS index from knowledge base documents"""
        logger.info("Building FAISS index from knowledge base...")
        
        # Load documents
        self.documents = load_kb_documents(self.kb_path)
        logger.info(f"Loaded {len(self.documents)} document chunks")
        
        if not self.documents:
            logger.warning("No documents found in knowledge base")
            # Create empty index
            self.index = faiss.IndexFlatIP(self.dimension)
            return
        
        # Generate embeddings
        texts = [doc['content'] for doc in self.documents]
        self.document_embeddings = embedding_model.encode(texts)
        
        # Create FAISS index
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(self.document_embeddings.astype(np.float32))
        
        logger.info(f"Index built with {self.index.ntotal} vectors")
        
        # Save index
        self.save()
    
    def search(self, query: str, top_k: int = 3) -> Tuple[List[Dict[str, Any]], float]:
        """Search for similar documents"""
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Index is empty")
            return [], 0.0
        
        try:
            # Encode query
            query_embedding = embedding_model.encode(query)
            
            # Search
            scores, indices = self.index.search(
                query_embedding.reshape(1, -1).astype(np.float32),
                min(top_k, self.index.ntotal)
            )
            
            # Get documents
            results = []
            for idx, score in zip(indices[0], scores[0]):
                if idx < len(self.documents):
                    doc = self.documents[idx].copy()
                    doc['similarity_score'] = float(score)
                    results.append(doc)
            
            # Calculate confidence (average score)
            confidence = float(np.mean(scores[0])) if len(scores[0]) > 0 else 0.0
            
            return results, confidence
            
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return [], 0.0
    
    def save(self):
        """Save index and documents"""
        if self.index is None:
            return
        
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_path))
            
            # Save documents and embeddings
            metadata_path = self.index_path.with_suffix('.pkl')
            with open(metadata_path, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'embeddings': self.document_embeddings
                }, f)
            
            logger.info(f"Index saved to {self.index_path}")
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def load(self):
        """Load index and documents"""
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_path))
            
            # Load documents and embeddings
            metadata_path = self.index_path.with_suffix('.pkl')
            with open(metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.documents = data.get('documents', [])
                self.document_embeddings = data.get('embeddings', None)
            
            logger.info(f"Index loaded with {self.index.ntotal} vectors")
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            self.index = None
            self.documents = []
            self.document_embeddings = None

# Global instance
vector_store = VectorStore()