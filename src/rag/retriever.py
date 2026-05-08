"""
Document retriever with ranking and filtering
"""
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass

from src.rag.vector_store import get_vector_store
from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class RetrievedDocument:
    """Container for a retrieved document with metadata"""
    content: str
    score: float  # Similarity score (0-1, higher is better)
    metadata: Dict
    id: str
    
    def __repr__(self):
        return f"RetrievedDocument(score={self.score:.3f}, id={self.id})"


class DocumentRetriever:
    """Retrieve and rank documents from vector store"""
    
    def __init__(self):
        self.vector_store = get_vector_store()
        self.similarity_threshold = settings.similarity_threshold
        self.top_k = settings.similarity_top_k
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        category_filter: Optional[str] = None,
        min_score: Optional[float] = None
    ) -> List[RetrievedDocument]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: Search query
            top_k: Number of results (uses config default if None)
            category_filter: Filter by document category
            min_score: Minimum similarity score threshold
            
        Returns:
            List of retrieved documents sorted by relevance
        """
        top_k = top_k or self.top_k
        min_score = min_score or self.similarity_threshold
        
        # Build metadata filter
        where = None
        if category_filter:
            where = {"category": category_filter}
        
        # Search vector store
        results = self.vector_store.search(
            query=query,
            n_results=top_k,
            where=where
        )
        
        # Parse results
        documents = []
        for i in range(len(results['ids'][0])):
            # ChromaDB returns distances, convert to similarity scores
            # Distance in cosine space: 0 = identical, 2 = opposite
            # Convert to similarity: 1 - (distance / 2)
            distance = results['distances'][0][i]
            score = 1 - (distance / 2)
            
            # Filter by minimum score
            if score < min_score:
                continue
            
            doc = RetrievedDocument(
                content=results['documents'][0][i],
                score=score,
                metadata=results['metadatas'][0][i] or {},
                id=results['ids'][0][i]
            )
            documents.append(doc)
        
        logger.info(f"Retrieved {len(documents)} documents (min_score={min_score:.2f})")
        return documents
    
    def format_context(self, documents: List[RetrievedDocument]) -> str:
        """
        Format retrieved documents into context string for LLM
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(
                f"[Document {i}] (Relevance: {doc.score:.2%})\n"
                f"{doc.content}\n"
            )
        
        return "\n".join(context_parts)
    
    def get_best_match(self, query: str) -> Optional[RetrievedDocument]:
        """
        Get single best matching document
        
        Args:
            query: Search query
            
        Returns:
            Best matching document or None
        """
        results = self.retrieve(query, top_k=1)
        return results[0] if results else None


# Global instance
_retriever = None


def get_retriever() -> DocumentRetriever:
    """Get or create the global retriever instance"""
    global _retriever
    if _retriever is None:
        _retriever = DocumentRetriever()
    return _retriever