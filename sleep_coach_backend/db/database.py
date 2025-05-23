import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
from typing import AsyncGenerator

# Load environment variables from .env file at the project root
# Assuming this file (database.py) is in sleep_coach_backend/db/
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Default to a local PostgreSQL DB if not set in .env
# Example format: "postgresql+asyncpg://user:password@host:port/dbname"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/sleep_coach_db")

async_engine = create_async_engine(
    DATABASE_URL,
    echo=True, # Log SQL queries, useful for debugging
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

# Dependency to get DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit() # Commit session if no exceptions
        except Exception:
            await session.rollback() # Rollback on error
            raise
        finally:
            await session.close() 