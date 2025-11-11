import importlib.util
import sys
from pathlib import Path

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _load_launcher_module():
    """Importa ``abpm_launcher`` desde disco, forzando su recarga."""

    module_name = "abpm_launcher"
    if module_name in sys.modules:
        del sys.modules[module_name]

    launcher_path = Path(__file__).resolve().parents[1] / "abpm_launcher.py"
    spec = importlib.util.spec_from_file_location(module_name, launcher_path)
    assert spec and spec.loader, "No se pudo cargar el módulo abpm_launcher"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def _reconfigure_database(monkeypatch, tmp_path):
    from app.core import config
    from app.core import database as db_module

    database_path = tmp_path / "abpm.db"
    storage_dir = tmp_path / "storage"

    monkeypatch.setattr(config.settings, "database_url", f"sqlite+aiosqlite:///{database_path}", raising=False)
    monkeypatch.setattr(config.settings, "storage_dir", storage_dir, raising=False)

    await db_module.engine.dispose()
    db_module.engine = create_async_engine(config.settings.database_url, echo=False, future=True)
    db_module.async_session_factory = async_sessionmaker(db_module.engine, expire_on_commit=False)

    return db_module, storage_dir


@pytest.mark.anyio
async def test_setup_creates_user_table(monkeypatch, tmp_path):
    """The launcher must import models before creating tables."""

    db_module, storage_dir = await _reconfigure_database(monkeypatch, tmp_path)

    module = _load_launcher_module()

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


@pytest.mark.anyio
async def test_create_user_populates_tables(monkeypatch, tmp_path):
    """El comando de creación de usuarios debe crear la tabla si no existe."""

    db_module, storage_dir = await _reconfigure_database(monkeypatch, tmp_path)
    module = _load_launcher_module()

    from app.core import security as security_module

    monkeypatch.setattr(security_module, "get_password_hash", lambda _: "hashed", raising=False)

    created = await module._create_user(
        email="test@example.com",
        password="secret123",
        full_name="Test User",
    )

    assert created is True
    assert storage_dir.exists()

    from app.models import User

    async with db_module.async_session_factory() as session:
        result = await session.execute(select(User).where(User.email == "test@example.com"))
        stored = result.scalar_one_or_none()

    assert stored is not None, "El usuario debería haberse insertado tras crear la tabla automáticamente"


@pytest.mark.anyio
async def test_create_user_retries_after_missing_table(monkeypatch, tmp_path):
    """Si la tabla desaparece tras la inicialización, el comando debe recrearla automáticamente."""

    db_module, storage_dir = await _reconfigure_database(monkeypatch, tmp_path)
    module = _load_launcher_module()

    from app.core import security as security_module
    from app.core.database import Base
    from sqlalchemy.exc import OperationalError
    from contextlib import asynccontextmanager

    # Aseguramos que la tabla exista inicialmente y luego la eliminamos para forzar el error.
    await module._initialize_database()
    async with db_module.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    monkeypatch.setattr(security_module, "get_password_hash", lambda _: "hashed", raising=False)

    real_factory = db_module.async_session_factory

    first_call = {"raised": False}

    @asynccontextmanager
    async def flaky_session():
        async with real_factory() as session:
            if not first_call["raised"]:
                original_execute = session.execute

                async def failing_execute(*args, **kwargs):
                    first_call["raised"] = True
                    raise OperationalError("SELECT", {}, Exception("no such table: users"))

                session.execute = failing_execute
                try:
                    yield session
                finally:
                    session.execute = original_execute
            else:
                yield session

    monkeypatch.setattr(db_module, "async_session_factory", lambda: flaky_session(), raising=False)

    created = await module._create_user(
        email="retry@example.com",
        password="secret123",
        full_name="Retry User",
    )

    assert created is True
    assert storage_dir.exists()

    from app.models import User

    async with db_module.async_session_factory() as session:
        result = await session.execute(select(User).where(User.email == "retry@example.com"))
        stored = result.scalar_one_or_none()

    assert stored is not None, "El usuario debería crearse tras reintentar la inicialización"
