"""Base SQLAlchemy model and session management."""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator

Base = declarative_base()

# Global engine and session factory (initialized in main.py)
async_engine = None
async_session_factory = None


def init_db(database_url: str):
    """Initialize the database engine and session factory."""
    global async_engine, async_session_factory
    
    # Convert postgresql:// to postgresql+asyncpg://
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    async_engine = create_async_engine(
        database_url,
        echo=False,  # Set to True for SQL query logging
        poolclass=NullPool,  # Use NullPool for async engines to avoid connection issues
    )
    
    async_session_factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    if async_session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all tables defined in models. Use Alembic for production."""
    if async_engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    async with async_engine.begin() as conn:
        # checkfirst=True is implicit in create_all but let's be explicit
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)


async def close_db():
    """Close the database engine."""
    global async_engine
    if async_engine:
        await async_engine.dispose()
        async_engine = None
