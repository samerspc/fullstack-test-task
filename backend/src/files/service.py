from __future__ import annotations

import mimetypes
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from src.core.config import get_settings
from src.core.exceptions import EmptyUpload, FileNotFound, StoredBlobMissing
from src.core.storage import FileStorage
from src.files.models import ProcessingStatus, StoredFile
from src.files.repository import FileRepository


@dataclass(slots=True, frozen=True)
class NewFilePayload:
    """Data handed off to the background pipeline after upload.

    Carrying everything the worker needs in the task args removes the extra
    SELECT it would otherwise do just to read immutable columns.
    """

    file_id: str
    size: int
    mime_type: str
    extension: str


class FileService:
    """Business logic for file management. Framework-agnostic."""

    def __init__(self, repo: FileRepository, storage: FileStorage) -> None:
        self._repo = repo
        self._storage = storage
        self._settings = get_settings()

    async def list_files(self) -> Sequence[StoredFile]:
        return await self._repo.list_all()

    async def get_file(self, file_id: str) -> StoredFile:
        file_item = await self._repo.get(file_id)
        if file_item is None:
            raise FileNotFound()
        return file_item

    async def create_file(self, title: str, upload: UploadFile) -> tuple[StoredFile, NewFilePayload]:
        file_id = str(uuid4())
        original_name = upload.filename or file_id
        suffix = Path(original_name).suffix
        stored_name = f"{file_id}{suffix}"

        try:
            blob = self._storage.save(
                source=upload.file,
                stored_name=stored_name,
                chunk_size=self._settings.upload_chunk_size,
            )
        except ValueError as err:
            raise EmptyUpload() from err

        mime_type = (
            upload.content_type
            or mimetypes.guess_type(stored_name)[0]
            or "application/octet-stream"
        )

        file_item = StoredFile(
            id=file_id,
            title=title,
            original_name=original_name,
            stored_name=stored_name,
            mime_type=mime_type,
            size=blob.size,
            processing_status=ProcessingStatus.UPLOADED,
        )
        await self._repo.add(file_item)
        await self._repo.commit()
        await self._repo.refresh(file_item)

        payload = NewFilePayload(
            file_id=file_id,
            size=blob.size,
            mime_type=mime_type,
            extension=suffix.lower(),
        )
        return file_item, payload

    async def rename(self, file_id: str, title: str) -> StoredFile:
        file_item = await self.get_file(file_id)
        file_item.title = title
        await self._repo.commit()
        await self._repo.refresh(file_item)
        return file_item

    async def delete(self, file_id: str) -> None:
        file_item = await self.get_file(file_id)
        stored_name = file_item.stored_name
        await self._repo.delete(file_item)
        await self._repo.commit()
        self._storage.delete(stored_name)

    async def resolve_download(self, file_id: str) -> tuple[StoredFile, Path]:
        file_item = await self.get_file(file_id)
        if not self._storage.exists(file_item.stored_name):
            raise StoredBlobMissing()
        return file_item, self._storage.path_of(file_item.stored_name)
