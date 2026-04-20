from __future__ import annotations

from pathlib import Path
from typing import Any


def extract(path: Path, mime_type: str, extension: str, size: int) -> dict[str, Any]:
    """Pure metadata extraction identical in behaviour to the original task."""
    metadata: dict[str, Any] = {
        "extension": extension.lower(),
        "size_bytes": size,
        "mime_type": mime_type,
    }

    if mime_type.startswith("text/"):
        content = path.read_text(encoding="utf-8", errors="ignore")
        metadata["line_count"] = len(content.splitlines())
        metadata["char_count"] = len(content)
    elif mime_type == "application/pdf":
        content = path.read_bytes()
        metadata["approx_page_count"] = max(content.count(b"/Type /Page"), 1)

    return metadata
