from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.files.models import StoredFile


class FileRepository:
    """Async repository used by HTTP handlers."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> Sequence[StoredFile]:
        result = await self._session.execute(
            select(StoredFile).order_by(StoredFile.created_at.desc())
        )
        return result.scalars().all()

    async def get(self, file_id: str) -> StoredFile | None:
        return await self._session.get(StoredFile, file_id)

    async def add(self, file_item: StoredFile) -> None:
        self._session.add(file_item)

    async def delete(self, file_item: StoredFile) -> None:
        await self._session.delete(file_item)

    async def commit(self) -> None:
        await self._session.commit()

    async def refresh(self, file_item: StoredFile) -> None:
        await self._session.refresh(file_item)


class SyncFileRepository:
    """Sync repository used by the Celery worker.

    Celery's prefork worker is single-threaded per task; async SQLAlchemy only
    adds an event loop and coroutine overhead there.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, file_id: str) -> StoredFile | None:
        return self._session.get(StoredFile, file_id)

    def commit(self) -> None:
        self._session.commit()
