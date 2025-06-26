import os
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

POSTGRES_URI = os.getenv("POSTGRES_URI")

if not POSTGRES_URI:
    raise ValueError("No POSTGRES_URI found in environment variables")

# The engine is the entry point to the database.
# echo=True is useful for debugging to see the generated SQL.
engine = create_async_engine(
    POSTGRES_URI,
    echo=True,
    pool_size=10,  # Default is 10
    max_overflow=20,  # Default is 10
    pool_recycle=600,  # Recycle connections after 10 minutes (adjust based on DB timeout)
    pool_pre_ping=True,  # Ensures connections are alive before use (some overhead)
)

# The sessionmaker provides a factory for creating Session objects.
# We will use this to get a session in our dependency.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Good practice for async sessions
    autoflush=False,
)


# A base class for our declarative models
class Base(DeclarativeBase):
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)

    created_at = Column(DateTime, default=datetime.now)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)


# Dependency to get a DB session
# This is the key to our modular approach.
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
