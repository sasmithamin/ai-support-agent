"""
Knowledge base search tool using RAG
"""
from typing import Optional
from langchain.tools import BaseTool
from pydantic import Field
import logging

from src.rag.retriever import get_retriever

logger = logging.getLogger(__name__)


class KnowledgeSearchTool(BaseTool):
    """Tool for searching the internal knowledge base"""
    
    name: str = "knowledge_search"
    description: str = (
        "Search the internal knowledge base for information. "
        "Use this to find answers from company documentation, FAQs, "
        "troubleshooting guides, and product information. "
        "Input should be a search query describing what you're looking for."
    )
    
    retriever: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.retriever = get_retriever()
    
    def _run(self, query: str) -> str:
        """
        Execute the search
        
        Args:
            query: Search query
            
        Returns:
            Formatted search results
        """
        try:
            logger.info(f"Searching knowledge base for: '{query}'")
            
            # Retrieve documents
            documents = self.retriever.retrieve(query)
            
            if not documents:
                return (
                    "No relevant information found in the knowledge base. "
                    "Consider using web_search for external information or "
                    "escalating to a human agent."
                )
            
            # Format results
            results = ["Found the following relevant information:\n"]
            
            for i, doc in enumerate(documents, 1):
                results.append(
                    f"\n{i}. [Relevance: {doc.score:.1%}]\n"
                    f"{doc.content}\n"
                )
                
                # Add source if available
                if 'source' in doc.metadata:
                    results.append(f"Source: {doc.metadata['source']}\n")
            
            return "".join(results)
            
        except Exception as e:
            logger.error(f"Knowledge search error: {e}")
            return f"Error searching knowledge base: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async version (calls sync for now)"""
        return self._run(query)


def get_knowledge_search_tool() -> KnowledgeSearchTool:
    """Get knowledge search tool instance"""
    return KnowledgeSearchTool()