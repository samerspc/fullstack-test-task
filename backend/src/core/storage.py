from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from src.core.config import get_settings


@dataclass(slots=True, frozen=True)
class SavedBlob:
    """Result of a successful blob save operation."""

    stored_name: str
    path: Path
    size: int


class FileStorage(ABC):
    """Abstraction over persistent binary storage.

    Concrete implementations may back onto the local filesystem today and S3
    tomorrow; the domain service only depends on this interface.
    """

    @abstractmethod
    def save(self, source: BinaryIO, stored_name: str, chunk_size: int) -> SavedBlob: ...

    @abstractmethod
    def path_of(self, stored_name: str) -> Path: ...

    @abstractmethod
    def exists(self, stored_name: str) -> bool: ...

    @abstractmethod
    def delete(self, stored_name: str) -> None: ...


class LocalFileStorage(FileStorage):
    """Local filesystem storage that streams uploads chunk-by-chunk.

    Streaming avoids loading the whole payload into memory, which is the main
    non-obvious memory win over the original ``await upload_file.read()``.
    """

    def __init__(self, root: Path) -> None:
        self._root = root
        self._root.mkdir(parents=True, exist_ok=True)

    def save(self, source: BinaryIO, stored_name: str, chunk_size: int) -> SavedBlob:
        target = self._root / stored_name
        size = 0
        with target.open("wb") as destination:
            while True:
                chunk = source.read(chunk_size)
                if not chunk:
                    break
                destination.write(chunk)
                size += len(chunk)
        if size == 0:
            target.unlink(missing_ok=True)
            raise ValueError("empty upload")
        return SavedBlob(stored_name=stored_name, path=target, size=size)

    def path_of(self, stored_name: str) -> Path:
        return self._root / stored_name

    def exists(self, stored_name: str) -> bool:
        return self.path_of(stored_name).exists()

    def delete(self, stored_name: str) -> None:
        self.path_of(stored_name).unlink(missing_ok=True)

    @classmethod
    def from_settings(cls) -> "LocalFileStorage":
        return cls(get_settings().storage_dir)


def get_file_storage() -> FileStorage:
    """FastAPI dependency providing the configured storage backend."""
    return LocalFileStorage.from_settings()


__all__ = ["FileStorage", "LocalFileStorage", "SavedBlob", "get_file_storage"]
