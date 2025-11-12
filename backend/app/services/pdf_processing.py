from __future__ import annotations

from pathlib import Path


class PDFProcessor:
    """Very small PDF processor placeholder."""

    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, filename: str, data: bytes) -> Path:
        path = self.storage_dir / filename
        path.write_bytes(data)
        return path
