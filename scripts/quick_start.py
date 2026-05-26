"""
Quick start script - Sets up everything and runs the server
"""
import asyncio
import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def quick_start():
    """Complete setup and start the server"""
    try:
        print("\n" + "=" * 80)
        print("🚀 AI SUPPORT AGENT - QUICK START")
        print("=" * 80 + "\n")
        
        # Step 1: Setup database
        print("📊 Step 1/3: Setting up database...")
        from scripts.setup_db import setup_database
        if await setup_database():
            print("✅ Database setup complete\n")
        else:
            print("❌ Database setup failed\n")
            return
        
        # Step 2: Load knowledge base
        print("📚 Step 2/3: Loading knowledge base...")
        from scripts.load_knowledge import load_knowledge_base
        if await load_knowledge_base():
            print("✅ Knowledge base loaded\n")
        else:
            print("❌ Knowledge base loading failed\n")
            return
        
        # Step 3: Run server
        print("🌐 Step 3/3: Starting server...")
        print("\n" + "=" * 80)
        print("✅ Setup complete! Starting server...\n")
        
        from scripts.run_server import run_server
        run_server()
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutdown requested. Goodbye!")
    except Exception as e:
        logger.error(f"❌ Quick start failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(quick_start())