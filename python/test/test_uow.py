import os

import pytest_asyncio
from databases import Database

from uow.databases import DatabasesUnitOfWork


async def get_conn():
    db = Database(
        f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/test"
    )
    await db.connect()
    return db


@pytest_asyncio.fixture(scope="function", loop_scope="function")  # type: ignore
async def db_conn():
    db = await get_conn()
    query = """CREATE TABLE IF NOT EXISTS Person (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100),
                balance INTEGER
            );"""
    await db.execute(query)  # type: ignore
    yield db
    await db.disconnect()


@pytest_asyncio.fixture(scope="function", loop_scope="function")  # type: ignore
async def database(db_conn: Database):
    yield db_conn
    query = "DELETE FROM Person;"
    await db_conn.execute(query)  # type: ignore


async def test_uow_rollback_when_no_commit(database: Database):
    uow = DatabasesUnitOfWork(database)
    async with uow:
        query = "INSERT INTO Person (id, name, balance) VALUES (1, 'John Doe', 100);"
        await database.execute(query)  # type: ignore
    query = "SELECT count(*) FROM Person;"
    assert await database.fetch_val(query) == 0  # type: ignore


async def test_uow_persists_when_commited(database: Database):
    uow = DatabasesUnitOfWork(database)
    async with uow:
        query = "INSERT INTO Person (id, name, balance) VALUES (1, 'John Doe', 100);"
        await database.execute(query)  # type: ignore
        await uow.commit()
    query = "SELECT count(*) FROM Person;"
    assert await database.fetch_val(query) == 1  # type: ignore
