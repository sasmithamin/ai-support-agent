from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# PostgreSQL async engine with connection pooling
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,         # Log SQL queries (disable in production)
    future=True,
    
    # PostgreSQL Connection Pool Settings
    pool_size=10,                # Keep 10 connections open
    max_overflow=20,             # Allow 20 extra connections under heavy load
    pool_pre_ping=True,          # Test connection before using (handles dropped connections)
    pool_recycle=3600,           # Recycle connections every hour
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db():
    """
    Dependency for FastAPI routes
    Provides database session and handles commit/rollback
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database - creates all tables
    Called on application startup
    """
    from src.db.models import Base
    
    try:
        async with engine.begin() as conn:
            # Creates tables if they don't exist
            # Does NOT drop existing tables
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ PostgreSQL database initialized successfully")
        logger.info(f"📊 Connected to: {settings.database_url.split('@')[1]}")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def check_db_connection():
    """
    Check if database connection is working
    Useful for health checks
    """
    try:
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


async def close_db():
    """
    Close database connections
    Called on application shutdown
    """
    await engine.dispose()
    logger.info("Database connections closed")