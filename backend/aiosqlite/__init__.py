"""Minimal async sqlite wrapper used as a fallback when the real aiosqlite package is unavailable.

This implementation provides the subset of the `aiosqlite` API that SQLAlchemy's
`sqlite+aiosqlite` dialect relies on. It executes all SQLite operations in a single
thread via :func:`asyncio.to_thread`, ensuring event loop responsiveness without
requiring the external dependency.
"""

from __future__ import annotations

import asyncio
import sqlite3
from typing import Any, Iterable, Optional, Sequence

__all__ = [
    "connect",
    "Connection",
    "Cursor",
    "Error",
    "DatabaseError",
    "IntegrityError",
    "NotSupportedError",
    "OperationalError",
    "ProgrammingError",
    "PARSE_DECLTYPES",
    "PARSE_COLNAMES",
    "Binary",
]

# Re-export DB-API compatible attributes expected by SQLAlchemy.
Error = sqlite3.Error
DatabaseError = sqlite3.DatabaseError
IntegrityError = sqlite3.IntegrityError
NotSupportedError = sqlite3.NotSupportedError
OperationalError = sqlite3.OperationalError
ProgrammingError = sqlite3.ProgrammingError
PARSE_DECLTYPES = sqlite3.PARSE_DECLTYPES
PARSE_COLNAMES = sqlite3.PARSE_COLNAMES
Binary = sqlite3.Binary


class _AsyncCallQueue:
    """Queue that executes synchronous callables in a worker task.

    SQLAlchemy's dialect uses ``connection._tx.put_nowait((future, fn))`` when it
    needs to mutate connection state from outside the worker thread. We replicate
    that behaviour by running ``fn`` in a thread and resolving the provided
    ``future`` with the result.
    """

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def put_nowait(self, item: Sequence[Any]) -> None:
        future, function = item

        async def _run() -> None:
            try:
                result = await asyncio.to_thread(function)
            except Exception as exc:  # pragma: no cover - defensive
                if not future.done():
                    future.set_exception(exc)
            else:
                if not future.done():
                    future.set_result(result)

        self._loop.create_task(_run())


class Cursor:
    """Asynchronous wrapper over ``sqlite3.Cursor``."""

    def __init__(self, cursor: sqlite3.Cursor, lock: asyncio.Lock) -> None:
        self._cursor = cursor
        self._lock = lock
        self.arraysize = 1
        self.description = None
        self.lastrowid = None
        self.rowcount = -1

    async def execute(self, operation: str, parameters: Optional[Sequence[Any]] = None) -> "Cursor":
        async with self._lock:
            if parameters is None:
                await asyncio.to_thread(self._cursor.execute, operation)
            else:
                await asyncio.to_thread(self._cursor.execute, operation, parameters)
            self.description = self._cursor.description
            self.lastrowid = self._cursor.lastrowid
            self.rowcount = self._cursor.rowcount
        return self

    async def executemany(self, operation: str, seq_of_parameters: Iterable[Sequence[Any]]) -> "Cursor":
        async with self._lock:
            await asyncio.to_thread(self._cursor.executemany, operation, list(seq_of_parameters))
            self.description = None
            self.lastrowid = self._cursor.lastrowid
            self.rowcount = self._cursor.rowcount
        return self

    async def fetchone(self) -> Any:
        async with self._lock:
            return await asyncio.to_thread(self._cursor.fetchone)

    async def fetchmany(self, size: Optional[int] = None) -> Sequence[Any]:
        if size is None:
            size = self.arraysize
        async with self._lock:
            return await asyncio.to_thread(self._cursor.fetchmany, size)

    async def fetchall(self) -> Sequence[Any]:
        async with self._lock:
            return await asyncio.to_thread(self._cursor.fetchall)

    async def close(self) -> None:
        async with self._lock:
            await asyncio.to_thread(self._cursor.close)

    def setinputsizes(self, *inputsizes: Any) -> None:  # pragma: no cover - compatibility stub
        return None


class Connection:
    """Async-friendly SQLite connection."""

    def __init__(self, conn: sqlite3.Connection, loop: asyncio.AbstractEventLoop) -> None:
        self._conn = conn
        self._loop = loop
        self._lock = asyncio.Lock()
        self._tx = _AsyncCallQueue(loop)
        self._closed = False

    # Provide a ``daemon`` attribute so SQLAlchemy can set it without errors.
    daemon: bool = True

    # ------------------------------------------------------------------
    # Context manager helpers
    async def __aenter__(self) -> "Connection":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.close()

    # ------------------------------------------------------------------
    # Properties mirroring ``sqlite3.Connection``
    @property
    def isolation_level(self) -> Optional[str]:
        return self._conn.isolation_level

    @isolation_level.setter
    def isolation_level(self, value: Optional[str]) -> None:
        self._conn.isolation_level = value

    @property
    def row_factory(self):  # pragma: no cover - passthrough
        return self._conn.row_factory

    @row_factory.setter
    def row_factory(self, func):  # pragma: no cover - passthrough
        self._conn.row_factory = func

    # ------------------------------------------------------------------
    async def cursor(self) -> Cursor:
        async with self._lock:
            cursor = await asyncio.to_thread(self._conn.cursor)
        return Cursor(cursor, self._lock)

    async def execute(self, sql: str, parameters: Optional[Sequence[Any]] = None) -> Cursor:
        cursor = await self.cursor()
        await cursor.execute(sql, parameters)
        return cursor

    async def executemany(self, sql: str, seq_of_parameters: Iterable[Sequence[Any]]) -> Cursor:
        cursor = await self.cursor()
        await cursor.executemany(sql, seq_of_parameters)
        return cursor

    async def executescript(self, script: str) -> None:
        async with self._lock:
            await asyncio.to_thread(self._conn.executescript, script)

    async def commit(self) -> None:
        async with self._lock:
            await asyncio.to_thread(self._conn.commit)

    async def rollback(self) -> None:
        async with self._lock:
            await asyncio.to_thread(self._conn.rollback)

    async def close(self) -> None:
        if self._closed:
            return
        async with self._lock:
            await asyncio.to_thread(self._conn.close)
            self._closed = True

    async def interrupt(self) -> None:  # pragma: no cover - compatibility stub
        async with self._lock:
            await asyncio.to_thread(self._conn.interrupt)

    async def create_function(self, *args, **kwargs) -> None:
        async with self._lock:
            await asyncio.to_thread(self._conn.create_function, *args, **kwargs)

    async def create_aggregate(self, *args, **kwargs) -> None:  # pragma: no cover - rarely used
        async with self._lock:
            await asyncio.to_thread(self._conn.create_aggregate, *args, **kwargs)

    async def create_collation(self, *args, **kwargs) -> None:  # pragma: no cover - rarely used
        async with self._lock:
            await asyncio.to_thread(self._conn.create_collation, *args, **kwargs)

    def __getattr__(self, item: str) -> Any:  # pragma: no cover - passthrough
        return getattr(self._conn, item)


class _ConnectAwaitable:
    """Object returned by :func:`connect` that can be awaited.

    SQLAlchemy sets ``.daemon = True`` on this object before awaiting it, so we
    expose the attribute even though it is not used by the fallback implementation.
    """

    def __init__(self, database: str, **kwargs: Any) -> None:
        self._database = database
        self._kwargs = kwargs
        self.daemon = True

    def __await__(self):
        return self._connect().__await__()

    async def _connect(self) -> Connection:
        loop = asyncio.get_running_loop()
        kwargs = dict(self._kwargs)
        kwargs.setdefault("check_same_thread", False)
        conn = await asyncio.to_thread(sqlite3.connect, self._database, **kwargs)
        return Connection(conn, loop)


def connect(database: str, *args: Any, **kwargs: Any) -> _ConnectAwaitable:
    if args:
        raise TypeError("aiosqlite.connect() only accepts keyword arguments in this fallback implementation")
    return _ConnectAwaitable(database, **kwargs)
