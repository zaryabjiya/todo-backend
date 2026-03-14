import os
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
# Use asyncpg for async operations
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/todo_app")

# For Neon/Cloud databases, we need to handle SSL differently
# Remove sslmode from URL and pass it separately via connect_args
def parse_database_url(url: str) -> tuple[str, dict]:
    """
    Parse database URL and extract SSL settings for asyncpg
    Returns (clean_url, connect_args)
    """
    connect_args = {}
    
    if "?sslmode=require" in url:
        url = url.replace("?sslmode=require", "")
        connect_args = {"ssl": "require"}
    elif "?ssl=true" in url:
        url = url.replace("?ssl=true", "")
        connect_args = {"ssl": "require"}
    
    return url, connect_args

clean_database_url, connect_args = parse_database_url(DATABASE_URL)

# Create async engine
async_engine = create_async_engine(
    clean_database_url,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args=connect_args,
)

# Create sync engine for non-async operations
BASE_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
# Also clean sslmode from sync URL
sync_clean_url, _ = parse_database_url(BASE_DATABASE_URL)
sync_engine = create_engine(
    sync_clean_url,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Async session maker
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Sync session maker
SessionLocal = sessionmaker(
    bind=sync_engine,
    class_=Session,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_db() -> AsyncSession:
    """
    Async dependency to provide database session for FastAPI endpoints
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


def get_sync_db() -> Session:
    """
    Sync dependency to provide database session for FastAPI endpoints
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def create_tables():
    """
    Create all tables defined in the models
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
