# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
# from typing import Generator
# from .config import settings
# import logging

# logger = logging.getLogger(__name__)

# # Create engine with connection pooling
# engine = create_engine(
#     settings.DATABASE_URL,
#     pool_size=settings.DATABASE_POOL_SIZE,
#     max_overflow=settings.DATABASE_MAX_OVERFLOW,
#     pool_pre_ping=True,
#     echo=settings.DEBUG
# )

# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine
# )

# Base = declarative_base()


# def get_db() -> Generator[Session, None, None]:
#     """Dependency for getting database session."""
#     db = SessionLocal()
#     try:
#         yield db
#     except Exception as e:
#         logger.error(f"Database error: {str(e)}")
#         db.rollback()
#         raise
#     finally:
#         db.close()


# def get_redis():
#     """Dependency for getting Redis client."""
#     # To be implemented with redis-py
#     pass

from typing import AsyncGenerator
import logging

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from .config import settings

logger = logging.getLogger(__name__)

# --------------------------------------------------
# Async Engine
# --------------------------------------------------

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
)

# --------------------------------------------------
# Session
# --------------------------------------------------

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:

    async with AsyncSessionLocal() as db:

        try:
            yield db

        except Exception as e:

            logger.error(str(e))

            await db.rollback()

            raise

        finally:

            await db.close()


def get_redis():
    pass