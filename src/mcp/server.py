"""
MCP Server - Model Context Protocol server implementation
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.mcp.tools_registry import get_tools_registry
from src.utils.llm_factory import get_llm

logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP Server for tool orchestration and context management
    Coordinates between LLM, tools, and conversation context
    """
    
    def __init__(self):
        self.tools_registry = get_tools_registry()
        self.llm = get_llm()
        self.conversation_history: List[Dict[str, Any]] = []
    
    def add_to_history(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_context(self, max_messages: int = 10) -> str:
        """
        Get formatted conversation context
        
        Args:
            max_messages: Maximum number of recent messages to include
            
        Returns:
            Formatted context string
        """
        recent_history = self.conversation_history[-max_messages:]
        
        context_parts = []
        for msg in recent_history:
            role = msg['role'].upper()
            content = msg['content']
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def execute_tool_call(self, tool_name: str, tool_input: str) -> Dict[str, Any]:
        """
        Execute a tool and return structured result
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input for the tool
            
        Returns:
            Dictionary with tool execution results
        """
        try:
            logger.info(f"MCP executing tool: {tool_name}")
            
            result = self.tools_registry.execute_tool(tool_name, tool_input)
            
            return {
                "success": True,
                "tool": tool_name,
                "input": tool_input,
                "output": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                "success": False,
                "tool": tool_name,
                "input": tool_input,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_available_tools_description(self) -> str:
        """Get formatted description of available tools"""
        descriptions = self.tools_registry.get_tool_descriptions()
        
        parts = ["Available tools:"]
        for name, desc in descriptions.items():
            parts.append(f"\n- {name}: {desc}")
        
        return "\n".join(parts)
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get MCP server statistics"""
        return {
            "registered_tools": len(self.tools_registry.get_all_tools()),
            "tool_names": self.tools_registry.get_tool_names(),
            "conversation_length": len(self.conversation_history),
            "llm_model": getattr(self.llm, 'model_name', 'unknown')
        }


# Global MCP server instance
_mcp_server = None


def get_mcp_server() -> MCPServer:
    """Get or create the global MCP server instance"""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPServer()
        logger.info("MCP Server initialized")
    return _mcp_server