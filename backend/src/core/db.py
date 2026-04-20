from collections.abc import AsyncIterator, Iterator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.core.config import get_settings


class Base(DeclarativeBase):
    """Declarative base shared by every ORM model in the project."""


@lru_cache
def _async_engine():
    return create_async_engine(get_settings().database_url_async, pool_pre_ping=True)


@lru_cache
def _async_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(_async_engine(), expire_on_commit=False, class_=AsyncSession)


@lru_cache
def _sync_engine():
    # Used only inside Celery workers where each task is a single-threaded
    # unit of work and async SQLAlchemy would add overhead without benefit.
    return create_engine(get_settings().database_url_sync, pool_pre_ping=True, future=True)


@lru_cache
def _sync_session_factory() -> sessionmaker[Session]:
    return sessionmaker(_sync_engine(), expire_on_commit=False, class_=Session, future=True)


async def get_async_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: yields an AsyncSession scoped to a single request."""
    async with _async_session_factory()() as session:
        yield session


def sync_session_factory() -> sessionmaker[Session]:
    """Return the cached sync session factory used by Celery tasks."""
    return _sync_session_factory()


def get_sync_session() -> Iterator[Session]:
    """Context helper for Celery tasks. Use as ``with get_sync_session() as s:``."""
    with _sync_session_factory()() as session:
        yield session
