import pytest

import aiosqlite


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_embedded_aiosqlite_fallback(tmp_path):
    db_path = tmp_path / "test.db"
    conn = await aiosqlite.connect(str(db_path))

    async with conn:
        await conn.execute("CREATE TABLE demo (value INTEGER)")
        await conn.execute("INSERT INTO demo (value) VALUES (?)", (42,))
        cursor = await conn.execute("SELECT value FROM demo")
        rows = await cursor.fetchall()

    assert rows == [(42,)]
