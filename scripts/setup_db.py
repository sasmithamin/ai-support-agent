import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.db.database import init_db, AsyncSessionLocal, check_db_connection
from src.db import crud
from config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_database():
    """Initialize PostgreSQL database"""
    try:
        logger.info("=" * 60)
        logger.info("🐘 Setting Up PostgreSQL Database")
        logger.info("=" * 60)
        
        # Step 1: Check connection
        logger.info("\n📡 Step 1: Checking PostgreSQL connection...")
        if not await check_db_connection():
            logger.error("❌ Cannot connect to PostgreSQL!")
            logger.error("\nTroubleshooting:")
            logger.error("1. Is PostgreSQL running?")
            logger.error("   Windows: Start 'postgresql-x64-16' service")
            logger.error("   Mac: brew services start postgresql@16")
            logger.error("   Linux: sudo systemctl start postgresql")
            logger.error("2. Check DATABASE_URL in your .env file:")
            logger.error(f"   {settings.database_url}")
            return False
        
        logger.info("✅ PostgreSQL connection successful")
        
        # Step 2: Create tables
        logger.info("\n📊 Step 2: Creating database tables...")
        await init_db()
        logger.info("✅ Tables created")
        
        # Step 3: Create sample data
        logger.info("\n📝 Step 3: Creating sample ticket...")
        async with AsyncSessionLocal() as session:
            ticket = await crud.create_ticket(
                session=session,
                user_id="demo_user",
                subject="Test Ticket - System Initialized",
                description="Database setup successful.",
                user_email="demo@example.com",
                category="system"
            )
            logger.info(f"✅ Sample ticket created: {ticket.ticket_number}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ PostgreSQL setup complete!")
        logger.info(f"📊 Database: {settings.database_url.split('@')[-1]}")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}", exc_info=True)
        logger.error("\nCommon fixes:")
        logger.error("1. Check PostgreSQL is running")
        logger.error("2. Verify DATABASE_URL in .env")
        logger.error("3. Make sure database and user exist:")
        logger.error("   psql -U postgres")
        logger.error("   CREATE DATABASE support_db;")
        logger.error("   CREATE USER support_user WITH PASSWORD 'yourpassword';")
        logger.error("   GRANT ALL PRIVILEGES ON DATABASE support_db TO support_user;")
        return False


async def reset_database():
    """Reset all tables"""
    from src.db.database import engine
    from src.db.models import Base
    
    logger.warning("⚠️  Resetting database...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("Dropped all tables")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Recreated all tables")
    
    logger.info("✅ Database reset complete")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    
    if args.reset:
        response = input("Reset database? All data will be lost. (yes/no): ")
        if response.lower() == "yes":
            asyncio.run(reset_database())
            asyncio.run(setup_database())
    else:
        asyncio.run(setup_database())