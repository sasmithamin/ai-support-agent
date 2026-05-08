"""
Tools module - exports all available tools
"""
from src.tools.knowledge_search import get_knowledge_search_tool
from src.tools.web_search import get_web_search_tool
from src.tools.ticket_manager import get_ticket_manager_tool

__all__ = [
    'get_knowledge_search_tool',
    'get_web_search_tool',
    'get_ticket_manager_tool'
]


def get_all_tools():
    """Get all available tools as a list"""
    return [
        get_knowledge_search_tool(),
        get_web_search_tool(),
        get_ticket_manager_tool()
    ]