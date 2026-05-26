"""
Database setup script - Initialize tables and load initial data
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.db.database import init_db, AsyncSessionLocal
from src.db import crud
from config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_database():
    """Initialize database and create tables"""
    try:
        logger.info("Initializing database...")
        
        # Create all tables
        await init_db()
        
        logger.info("✅ Database initialized successfully!")
        logger.info(f"Database location: {settings.database_url}")
        
        # Create a test ticket
        async with AsyncSessionLocal() as session:
            logger.info("Creating sample ticket...")
            
            ticket = await crud.create_ticket(
                session=session,
                user_id="demo_user",
                subject="Test Ticket - System Initialized",
                description="This is a test ticket created during database setup.",
                user_email="demo@example.com",
                category="system"
            )
            
            logger.info(f"✅ Sample ticket created: {ticket.ticket_number}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}", exc_info=True)
        return False


async def reset_database():
    """Reset database - WARNING: Deletes all data"""
    from src.db.database import engine
    from src.db.models import Base
    
    logger.warning("⚠️  Resetting database - ALL DATA WILL BE DELETED")
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Dropped all tables")
            
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Recreated all tables")
        
        logger.info("✅ Database reset complete")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database setup utility")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset database (WARNING: deletes all data)"
    )
    
    args = parser.parse_args()
    
    if args.reset:
        response = input("Are you sure you want to reset the database? (yes/no): ")
        if response.lower() == "yes":
            asyncio.run(reset_database())
            asyncio.run(setup_database())
        else:
            logger.info("Database reset cancelled")
    else:
        asyncio.run(setup_database())