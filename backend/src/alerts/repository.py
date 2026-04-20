from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.alerts.models import Alert


class AlertRepository:
    """Async repository for the HTTP layer."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> Sequence[Alert]:
        result = await self._session.execute(select(Alert).order_by(Alert.created_at.desc()))
        return result.scalars().all()


class SyncAlertRepository:
    """Sync repository used from inside Celery tasks."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, alert: Alert) -> None:
        self._session.add(alert)
