from __future__ import annotations

import re
from pathlib import Path

SAFE_CHARS_RE = re.compile(r"[^A-Za-z0-9._-]")


def sanitize_upload_filename(filename: str) -> str:
    sanitized = SAFE_CHARS_RE.sub("_", filename)
    return sanitized or "upload.pdf"


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
