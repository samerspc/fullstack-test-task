"""Consolidated post-upload pipeline.

Key optimisations over the original three-task chain:

1. *One* Celery task (``process_uploaded_file``) instead of three chained via
   ``.delay``. That removes two broker round-trips and two task-bookkeeping
   writes per uploaded file.

2. *One* SELECT and *one* UPDATE commit per file. The original chain reloaded
   the same row in every task. Here we load it once, mutate everything the
   scan + metadata step requires, then commit.

3. *Sync* SQLAlchemy inside the worker. A Celery prefork worker runs one task
   at a time per process; async SQLAlchemy only forces us to spin an event
   loop and wrap every call in ``run_until_complete``. The original code kept
   a global ``_worker_loop`` just to paper over that. We drop both.

4. Scan inputs (``size``, ``mime_type``, ``extension``) are passed as task
   args, so the scan phase doesn't need to re-read the row just to look at
   immutable columns.
"""
from __future__ import annotations

from src.alerts.models import Alert, AlertLevel
from src.alerts.repository import SyncAlertRepository
from src.core.db import sync_session_factory
from src.core.storage import LocalFileStorage
from src.files.models import ProcessingStatus, ScanStatus, StoredFile
from src.files.repository import SyncFileRepository
from src.tasks.celery_app import celery_app
from src.tasks.metadata import extract
from src.tasks.scanner import scan


def _build_alert(file_item: StoredFile) -> Alert:
    if file_item.processing_status == ProcessingStatus.FAILED:
        return Alert(
            file_id=file_item.id,
            level=AlertLevel.CRITICAL,
            message="File processing failed",
        )
    if file_item.requires_attention:
        return Alert(
            file_id=file_item.id,
            level=AlertLevel.WARNING,
            message=f"File requires attention: {file_item.scan_details}",
        )
    return Alert(
        file_id=file_item.id,
        level=AlertLevel.INFO,
        message="File processed successfully",
    )


@celery_app.task(name="files.process_uploaded_file")
def process_uploaded_file(
    file_id: str,
    size: int,
    mime_type: str,
    extension: str,
) -> None:
    """Scan, extract metadata, persist results and raise an alert in one pass."""
    storage = LocalFileStorage.from_settings()
    factory = sync_session_factory()

    with factory() as session:
        files = SyncFileRepository(session)
        alerts = SyncAlertRepository(session)

        file_item = files.get(file_id)
        if file_item is None:
            return

        file_item.processing_status = ProcessingStatus.PROCESSING

        verdict = scan(size=size, mime_type=mime_type, extension=extension)
        file_item.scan_status = verdict.status
        file_item.scan_details = verdict.details
        file_item.requires_attention = verdict.suspicious

        stored_path = storage.path_of(file_item.stored_name)
        if not storage.exists(file_item.stored_name):
            file_item.processing_status = ProcessingStatus.FAILED
            file_item.scan_status = file_item.scan_status or ScanStatus.FAILED
            file_item.scan_details = "stored file not found during metadata extraction"
        else:
            file_item.metadata_json = extract(
                path=stored_path,
                mime_type=mime_type,
                extension=extension,
                size=size,
            )
            file_item.processing_status = ProcessingStatus.PROCESSED

        alerts.add(_build_alert(file_item))
        session.commit()
