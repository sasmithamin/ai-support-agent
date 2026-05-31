"""
FastAPI application main file
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config.settings import settings
from src.db.database import init_db
from src.api.routes import chat, tickets, knowledge

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Support Agent...")
    
    # Initialize database
    await init_db()
    
    # Verify connection
    from src.db.database import check_db_connection
    if await check_db_connection():
        logger.info("✅ PostgreSQL connection verified")
    else:
        logger.error("❌ PostgreSQL connection failed!")
    
    yield
    
    # Cleanup on shutdown
    from src.db.database import close_db
    await close_db()
    logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-Powered Customer Support Agent with RAG and MCP",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api")
app.include_router(tickets.router, prefix="/api")
app.include_router(knowledge.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Support Agent API",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )