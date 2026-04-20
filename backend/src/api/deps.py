from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.alerts.repository import AlertRepository
from src.alerts.service import AlertService
from src.core.db import get_async_session
from src.core.storage import FileStorage, get_file_storage
from src.files.repository import FileRepository
from src.files.service import FileService


def get_file_service(
    session: AsyncSession = Depends(get_async_session),
    storage: FileStorage = Depends(get_file_storage),
) -> FileService:
    return FileService(repo=FileRepository(session), storage=storage)


def get_alert_service(
    session: AsyncSession = Depends(get_async_session),
) -> AlertService:
    return AlertService(repo=AlertRepository(session))
