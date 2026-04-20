from __future__ import annotations

from dataclasses import dataclass

from src.core.config import get_settings


@dataclass(slots=True, frozen=True)
class ScanVerdict:
    """Pure result of scanning; no side effects and no ORM dependencies."""

    suspicious: bool
    details: str

    @property
    def status(self) -> str:
        return "suspicious" if self.suspicious else "clean"


def scan(size: int, mime_type: str, extension: str) -> ScanVerdict:
    """Run the same heuristics the original implementation did.

    Kept pure and side-effect-free so it is trivially unit-testable and the
    Celery task stays thin.
    """
    settings = get_settings()
    reasons: list[str] = []

    ext = extension.lower()
    if ext in set(settings.suspicious_extensions):
        reasons.append(f"suspicious extension {ext}")

    if size > settings.suspicious_size_bytes:
        reasons.append("file is larger than 10 MB")

    if ext == ".pdf" and mime_type not in {"application/pdf", "application/octet-stream"}:
        reasons.append("pdf extension does not match mime type")

    return ScanVerdict(
        suspicious=bool(reasons),
        details=", ".join(reasons) if reasons else "no threats found",
    )
