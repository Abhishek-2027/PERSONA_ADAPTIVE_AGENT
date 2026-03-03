from typing import List, Dict, Any, Tuple
from app.models.vector_store import vector_store
from app.utils.helpers import format_context
from app.utils.logger import logger
from app.config import config

class KnowledgeRetriever:
    """Retrieve relevant knowledge base content"""
    
    def __init__(self):
        """Initialize retriever with global vector store instance"""
        self.vector_store = vector_store
        self.confidence_threshold = config.ESCALATION_CONFIDENCE_THRESHOLD
    
    def search(self, query: str, top_k: int = 3) -> Tuple[List[Dict[str, Any]], float]:
        """Search for relevant documents"""
        results, confidence = self.vector_store.search(query, top_k)
        
        logger.info(f"Retrieved {len(results)} documents with confidence {confidence:.2f}")
        
        # Format results for use - with safe metadata access
        formatted_results = []
        for doc in results:
            # Safely access metadata with fallback
            metadata = doc.get("metadata", {})
            if not isinstance(metadata, dict):
                metadata = {}
            
            formatted_results.append({
                "title": doc.get("title", "Unknown"),
                "content": doc.get("content", ""),
                "source": doc.get("source", "Unknown"),
                "similarity": doc.get("similarity_score", 0.0),
                "category": metadata.get("category", "general")
            })
        
        return formatted_results, confidence
    
    def get_context_string(self, query: str) -> Tuple[str, float]:
        """Get formatted context string from search results"""
        results, confidence = self.search(query)
        context = format_context(results)
        return context, confidence

# Global instance
retriever = KnowledgeRetriever()