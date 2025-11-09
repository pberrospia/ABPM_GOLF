from __future__ import annotations

from pathlib import Path
import re
import unicodedata

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

    # Normalize unicode so accented characters don't produce filesystem surprises.
    candidate = unicodedata.normalize("NFKD", candidate)
    candidate = "".join(ch for ch in candidate if not unicodedata.combining(ch))

    # Strip surrounding whitespace and leading dots to avoid hidden files.
    candidate = candidate.strip().lstrip(".")

    # Replace characters outside a conservative whitelist (safe across OSes).
    candidate = re.sub(r"[^A-Za-z0-9._-]", "_", candidate)

    # Avoid extremely long names that could break filesystems.
    if len(candidate) > 255:
        suffix = Path(candidate).suffix
        if suffix:
            base = candidate[: len(candidate) - len(suffix)]
            max_base_len = 255 - len(suffix)
            if max_base_len <= 0:
                return fallback
            candidate = base[:max_base_len] + suffix
        else:
            candidate = candidate[:255]

    if candidate in {"", ".", ".."}:
        return fallback

    return candidate

