"""
Knowledge base management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from typing import List

from src.api.models.requests import KnowledgeUploadRequest
from src.api.models.responses import StatsResponse
from src.db.database import get_db
from src.rag.vector_store import get_vector_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/upload")
async def upload_knowledge(
    request: KnowledgeUploadRequest,
    db: AsyncSession = Depends(get_db)
):
    """Upload a knowledge document"""
    try:
        vector_store = get_vector_store()
        
        # Add to vector store
        vector_store.add_documents(
            documents=[request.content],
            metadatas=[{
                "title": request.title,
                "category": request.category,
                "source": request.source or "manual_upload"
            }]
        )
        
        logger.info(f"Uploaded knowledge: {request.title}")
        
        return {
            "message": "Knowledge document uploaded successfully",
            "title": request.title
        }
        
    except Exception as e:
        logger.error(f"Error uploading knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_knowledge(
    query: str,
    top_k: int = 5
):
    """Search knowledge base"""
    try:
        vector_store = get_vector_store()
        results = vector_store.search(query, n_results=top_k)
        
        return {
            "query": query,
            "results": [
                {
                    "content": results['documents'][0][i],
                    "score": 1 - (results['distances'][0][i] / 2),
                    "metadata": results['metadatas'][0][i]
                }
                for i in range(len(results['ids'][0]))
            ]
        }
        
    except Exception as e:
        logger.error(f"Error searching knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get system statistics"""
    try:
        # Ticket stats
        ticket_stats = await crud.get_ticket_stats(db)
        
        # Vector store stats
        vector_store = get_vector_store()
        vector_stats = vector_store.get_stats()
        
        # MCP stats
        from src.mcp.server import get_mcp_server
        mcp = get_mcp_server()
        mcp_stats = mcp.get_stats()
        
        return StatsResponse(
            total_tickets=ticket_stats['total_tickets'],
            open_tickets=ticket_stats['open_tickets'],
            resolved_tickets=ticket_stats['resolved_tickets'],
            average_sentiment=ticket_stats['average_sentiment'],
            vector_store_documents=vector_stats['document_count'],
            registered_tools=mcp_stats['registered_tools']
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))