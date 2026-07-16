from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.pool import AsyncAdaptedQueuePool

from ..core.config import settings

# ==========================================================
# Engine
# ==========================================================

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=AsyncAdaptedQueuePool,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# ==========================================================
# Session Factory
# ==========================================================

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# ==========================================================
# Dependency
# ==========================================================

async def get_db():

    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_engine():
    return engine