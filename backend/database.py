"""
FORTIS SENTINEL - Database Configuration

Centralizes database engine, session factory, and declarative base.
All models import Base from here to avoid circular imports.
"""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import get_settings

# ---------------------------------------------------------------------------
# Declarative Base
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models."""
    pass


# ---------------------------------------------------------------------------
# Engine & Session
# ---------------------------------------------------------------------------

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.is_development,
    future=True,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
