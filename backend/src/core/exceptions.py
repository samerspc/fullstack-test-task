class DomainError(Exception):
    """Base class for domain-level errors that must not leak framework types."""

    status_code: int = 400
    detail: str = "Domain error"

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail or self.detail)
        if detail is not None:
            self.detail = detail


class FileNotFound(DomainError):
    status_code = 404
    detail = "File not found"


class StoredBlobMissing(DomainError):
    status_code = 404
    detail = "Stored file not found"


class EmptyUpload(DomainError):
    status_code = 400
    detail = "File is empty"
