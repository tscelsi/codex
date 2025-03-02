"""A simple example of using a unit of work to guarantee consistency across multiple
database actions.

NOTE: ensure you have a local PostgreSQL database running"""

import asyncpg  # type: ignore
from databases import Database

from uow.databases import DatabasesUnitOfWork


async def transaction_failing():
    """This example demonstrates how a transaction can be rolled back if an error
    occurs after the transaction has started."""
    async with Database("postgresql://root:password@localhost:5432/test") as database:
        uow = DatabasesUnitOfWork(database)
        try:
            async with uow:
                query = "CREATE TABLE IF NOT EXISTS Test (id INTEGER PRIMARY KEY);"
                await database.execute(query)  # type: ignore
                raise ValueError("Transaction failed")
        except ValueError:
            pass

        # this query will fail because the table 'Test' was not created, as the
        # transaction was rolled back
        query = "SELECT count(*) FROM Test;"
        try:
            await database.fetch_val(query) == 0  # type: ignore
        except asyncpg.exceptions.UndefinedTableError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(transaction_failing())
