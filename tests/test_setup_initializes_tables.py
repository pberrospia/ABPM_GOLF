import pytest
import importlib.util
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_setup_creates_user_table(monkeypatch, tmp_path):
    """The launcher must import models before creating tables."""

    # Reconfigure settings to point to a temporary database and storage directory.
    from app.core import config
    from app.core import database as db_module

    database_path = tmp_path / "abpm.db"
    storage_dir = tmp_path / "storage"

    monkeypatch.setattr(config.settings, "database_url", f"sqlite+aiosqlite:///{database_path}", raising=False)
    monkeypatch.setattr(config.settings, "storage_dir", storage_dir, raising=False)

    # Recreate the SQLAlchemy engine/session factory so they use the temporary database.
    await db_module.engine.dispose()
    db_module.engine = create_async_engine(config.settings.database_url, echo=False, future=True)
    db_module.async_session_factory = async_sessionmaker(db_module.engine, expire_on_commit=False)

    launcher_path = Path(__file__).resolve().parents[1] / "abpm_launcher.py"
    spec = importlib.util.spec_from_file_location("abpm_launcher", launcher_path)
    assert spec and spec.loader, "No se pudo cargar el módulo abpm_launcher"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    _initialize_database = module._initialize_database

    await _initialize_database()

    assert storage_dir.exists()

    async with db_module.engine.begin() as conn:
        result = await conn.run_sync(
            lambda sync_conn: sync_conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            ).fetchone()
        )

    assert result is not None, "La tabla 'users' debería existir después de ejecutar setup"
