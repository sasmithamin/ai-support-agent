"""
Web search tool using Tavily API
"""
from typing import Optional
from langchain.tools import BaseTool
from pydantic import Field
import logging
import os

logger = logging.getLogger(__name__)


class WebSearchTool(BaseTool):
    """Tool for searching the web using Tavily API"""
    
    name: str = "web_search"
    description: str = (
        "Search the internet for current information, recent updates, "
        "or topics not covered in the knowledge base. "
        "Use this when knowledge_search doesn't have the answer or "
        "when you need up-to-date information. "
        "Input should be a search query."
    )
    
    api_key: Optional[str] = Field(default=None, exclude=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from config.settings import settings
        self.api_key = settings.tavily_api_key
    
    def _run(self, query: str) -> str:
        """
        Execute web search
        
        Args:
            query: Search query
            
        Returns:
            Formatted search results
        """
        try:
            # Check if API key is configured
            if not self.api_key:
                return (
                    "Web search is not configured. Please add TAVILY_API_KEY "
                    "to your .env file. Get a free key at https://tavily.com"
                )
            
            logger.info(f"Searching web for: '{query}'")
            
            # Import here to avoid dependency if not configured
            from tavily import TavilyClient
            
            client = TavilyClient(api_key=self.api_key)
            
            # Perform search
            response = client.search(
                query=query,
                search_depth="basic",  # or "advanced" for more results
                max_results=5
            )
            
            # Format results
            if not response.get('results'):
                return f"No web results found for: {query}"
            
            results = ["Found the following information from the web:\n"]
            
            for i, result in enumerate(response['results'], 1):
                results.append(
                    f"\n{i}. {result.get('title', 'No title')}\n"
                    f"{result.get('content', 'No content')}\n"
                    f"Source: {result.get('url', 'No URL')}\n"
                )
            
            return "".join(results)
            
        except ImportError:
            return (
                "Tavily package not installed. "
                "Run: pip install tavily-python"
            )
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return f"Error performing web search: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async version"""
        return self._run(query)


def get_web_search_tool() -> WebSearchTool:
    """Get web search tool instance"""
    return WebSearchTool()