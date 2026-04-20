from __future__ import annotations

from collections.abc import Sequence

from src.alerts.models import Alert
from src.alerts.repository import AlertRepository


class AlertService:
    """Business logic for alerts. Framework-agnostic."""

    def __init__(self, repo: AlertRepository) -> None:
        self._repo = repo

    async def list_alerts(self) -> Sequence[Alert]:
        return await self._repo.list_all()
