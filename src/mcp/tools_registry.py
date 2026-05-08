"""
MCP Tools Registry - Register and manage tools
"""
from typing import List, Dict, Any, Optional
import logging
from langchain.tools import BaseTool

from src.tools import get_all_tools

logger = logging.getLogger(__name__)


class ToolsRegistry:
    """Registry for managing and accessing tools"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register all default tools"""
        for tool in get_all_tools():
            self.register_tool(tool)
    
    def register_tool(self, tool: BaseTool):
        """
        Register a tool
        
        Args:
            tool: LangChain tool to register
        """
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def get_all_tools(self) -> List[BaseTool]:
        """Get all registered tools"""
        return list(self.tools.values())
    
    def get_tool_names(self) -> List[str]:
        """Get names of all registered tools"""
        return list(self.tools.keys())
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all tools"""
        return {
            name: tool.description
            for name, tool in self.tools.items()
        }
    
    def execute_tool(self, name: str, input_data: str) -> str:
        """
        Execute a tool by name
        
        Args:
            name: Tool name
            input_data: Input for the tool
            
        Returns:
            Tool output
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        
        logger.info(f"Executing tool: {name}")
        return tool.run(input_data)


# Global registry instance
_registry = None


def get_tools_registry() -> ToolsRegistry:
    """Get or create the global tools registry"""
    global _registry
    if _registry is None:
        _registry = ToolsRegistry()
    return _registry