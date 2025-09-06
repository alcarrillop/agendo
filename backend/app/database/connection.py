"""
Database connection and session management.
Handles Supabase PostgreSQL connection using SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import get_settings
from app.models.database import Base
import logging

settings = get_settings()
logger = logging.getLogger(__name__)


# Create database engines
if settings.DATABASE_URL and settings.DATABASE_URL.startswith("postgresql"):
    # For production with full DATABASE_URL (PostgreSQL)
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
    ASYNC_SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
elif settings.DATABASE_URL and settings.DATABASE_URL.startswith("sqlite"):
    # For SQLite with async support
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
    ASYNC_SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
    logger.warning("Using SQLite database. Configure Supabase for production.")
elif settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
    # For Supabase connection
    # Extract connection details from Supabase URL
    supabase_host = settings.SUPABASE_URL.replace("https://", "").replace("http://", "")
    SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:{settings.SUPABASE_SERVICE_ROLE_KEY}@db.{supabase_host}:5432/postgres"
    ASYNC_SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://postgres:{settings.SUPABASE_SERVICE_ROLE_KEY}@db.{supabase_host}:5432/postgres"
else:
    # Fallback to local SQLite for development
    SQLALCHEMY_DATABASE_URL = "sqlite:///./agendo.db"
    ASYNC_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./agendo.db"
    logger.warning("Using SQLite database. Configure Supabase for production.")


# Create synchronous engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG  # Log SQL queries in debug mode
)

# Create asynchronous engine for async operations
async_engine = create_async_engine(
    ASYNC_SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Create session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


def create_tables():
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


async def create_tables_async():
    """Create all database tables asynchronously."""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully (async)")
    except Exception as e:
        logger.error(f"Error creating database tables (async): {e}")
        raise


def get_db() -> Session:
    """
    Dependency to get database session for synchronous operations.
    Use this in FastAPI endpoints that don't need async database operations.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncSession:
    """
    Dependency to get async database session.
    Use this in FastAPI endpoints that need async database operations.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


class DatabaseManager:
    """
    Database manager for handling common database operations.
    Provides both sync and async methods.
    """
    
    @staticmethod
    def get_session() -> Session:
        """Get a new database session."""
        return SessionLocal()
    
    @staticmethod
    async def get_async_session() -> AsyncSession:
        """Get a new async database session."""
        return AsyncSessionLocal()
    
    @staticmethod
    async def init_database():
        """Initialize the database and create tables."""
        await create_tables_async()
        logger.info("Database initialized successfully")
    
    @staticmethod
    async def close_connections():
        """Close all database connections."""
        await async_engine.dispose()
        engine.dispose()
        logger.info("Database connections closed")

