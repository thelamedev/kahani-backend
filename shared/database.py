import sys
import logging
import time
import os
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, event
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

POSTGRES_URI = os.getenv("POSTGRES_URI")

if not POSTGRES_URI:
    raise ValueError("No POSTGRES_URI found in environment variables")

query_duration_logger = logging.getLogger("sqlalchemy.engine").getChild("Timing")
query_duration_logger.addHandler(logging.StreamHandler(sys.stdout))

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

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        default=None,
    )


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


# @event.listens_for(engine.sync_engine, "before_cursor_execute", retval=True)
# def before_execute(conn, clauseelement, multiparams, params):
#     conn.info.setdefault("query_start_time", []).append(time.monotonic())
#     return clauseelement, multiparams, params


@event.listens_for(engine.sync_engine, "before_cursor_execute", retval=True)
def before_cursor_execute(
    conn,
    cursor,
    statement,
    parameters,
    context,
    executemany,
):
    """
    Listener to be called before a cursor is executed.
    Starts a timer and stores it in the connection's info dictionary.
    """
    _ = cursor
    _ = context
    _ = executemany

    # Use the connection's info dict to store the start time.
    # We use a stack to handle nested cursor executions (less common, but good practice).
    conn.info.setdefault("query_start_time", []).append(time.monotonic())
    # You can also log the query statement here if needed
    # query_duration_logger.debug("Starting query: %s", statement)
    return statement, parameters


@event.listens_for(engine.sync_engine, "after_cursor_execute")
def after_cursor_execute(
    conn,
    cursor,
    statement,
    parameters,
    context,
    executemany,
):
    """
    Listener to be called after a cursor has been executed.
    Calculates the duration and logs it.
    """
    _ = cursor
    _ = context
    _ = executemany

    # Pop the start time from the stack
    total_time = time.monotonic() - conn.info["query_start_time"].pop()

    # Log the query, parameters, and its duration.
    # We use a more descriptive log message for clarity.
    query_duration_logger.info(
        "Query completed in %.4f ms. Statement: %s. Parameters: %s",
        total_time * 1000,
        statement,
        parameters,
    )

    print(
        f"{datetime.now().isoformat()} [QUERY_DURATION] Query completed in {total_time:.4f} ms. Statement: {statement}. Parameters: {parameters}"
    )
    return statement, parameters
