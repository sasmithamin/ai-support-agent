"""
Run the FastAPI server with proper setup
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_server():
    """Run the FastAPI server"""
    logger.info("=" * 80)
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info("=" * 80)
    logger.info(f"\n📍 Server: http://{settings.host}:{settings.port}")
    logger.info(f"📚 Docs: http://{settings.host}:{settings.port}/docs")
    logger.info(f"🔧 Environment: {settings.environment}")
    logger.info(f"🤖 LLM: {'Local Ollama' if settings.use_local_llm else 'Cloud API'}")
    logger.info(f"🗄️  Database: {settings.database_url}")
    logger.info(f"📦 Vector DB: {settings.chroma_db_path}\n")
    logger.info("=" * 80 + "\n")
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    run_server()