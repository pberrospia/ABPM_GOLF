from __future__ import annotations

from pathlib import Path

import ntpath


def sanitize_upload_filename(filename: str | None, fallback: str = "upload") -> str:
    """Return a safe filename derived from user-provided input.

    The function removes any directory components and falls back to a
    predictable name when the resulting filename is empty or otherwise unsafe.
    """

    if not filename:
        return fallback

    # ``ntpath.basename`` handles Windows-style paths while ``Path.name`` covers POSIX.
    candidate = ntpath.basename(filename)
    candidate = Path(candidate).name

    if candidate in {"", ".", ".."}:
        return fallback

    return candidate

