from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import FileResponse

from src.api.deps import get_file_service
from src.files.schemas import FileItem, FileUpdate
from src.files.service import FileService
from src.tasks.pipeline import process_uploaded_file

router = APIRouter(prefix="/files", tags=["files"])


@router.get("", response_model=list[FileItem])
async def list_files(service: FileService = Depends(get_file_service)) -> list[FileItem]:
    files = await service.list_files()
    return [FileItem.model_validate(f) for f in files]


@router.post("", response_model=FileItem, status_code=status.HTTP_201_CREATED)
async def create_file(
    title: str = Form(..., min_length=1, max_length=255),
    file: UploadFile = File(...),
    service: FileService = Depends(get_file_service),
) -> FileItem:
    file_item, payload = await service.create_file(title=title, upload=file)
    process_uploaded_file.delay(
        payload.file_id,
        payload.size,
        payload.mime_type,
        payload.extension,
    )
    return FileItem.model_validate(file_item)


@router.get("/{file_id}", response_model=FileItem)
async def get_file(
    file_id: str,
    service: FileService = Depends(get_file_service),
) -> FileItem:
    file_item = await service.get_file(file_id)
    return FileItem.model_validate(file_item)


@router.patch("/{file_id}", response_model=FileItem)
async def update_file(
    file_id: str,
    payload: FileUpdate,
    service: FileService = Depends(get_file_service),
) -> FileItem:
    file_item = await service.rename(file_id=file_id, title=payload.title)
    return FileItem.model_validate(file_item)


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    service: FileService = Depends(get_file_service),
) -> FileResponse:
    file_item, path = await service.resolve_download(file_id)
    return FileResponse(path=path, media_type=file_item.mime_type, filename=file_item.original_name)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: str,
    service: FileService = Depends(get_file_service),
) -> None:
    await service.delete(file_id)
