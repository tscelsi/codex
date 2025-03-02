import os

import pytest_asyncio


def pytest_configure():
    os.environ["PYTEST"] = "true"
    os.environ["DB_HOST"] = "localhost"
    os.environ["DB_PORT"] = "5432"
    os.environ["DB_USER"] = "root"
    os.environ["DB_PASS"] = "password"


@pytest_asyncio.fixture(scope="package", loop_scope="package")
async def database():
    from databases import Database

    db = Database(
        f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/test"
    )
    await db.connect()
    query = """CREATE TABLE Person (id INTEGER PRIMARY KEY, name VARCHAR(100));"""
    await db.execute(query)  # type: ignore
    yield db
    await db.disconnect()
