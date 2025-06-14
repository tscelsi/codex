from databases import Database

from .base import AbstractUnitOfWork, UnitOfWorkError


class DatabasesUnitOfWork(AbstractUnitOfWork):
    def __init__(self, database: Database):
        self._database = database
        self._transaction = None
        self.committed = False

    async def __aenter__(
        self, isolation: str | None = None
    ) -> AbstractUnitOfWork:
        self._transaction = await self._database.transaction(
            isolation=isolation
        )
        return await super().__aenter__()

    async def __aexit__(
        self, exc_type: type, exc_val: Exception, exc_tb: object
    ):
        await self.rollback()

    async def rollback(self):
        if self._transaction is None:
            raise UnitOfWorkError("rollback() not called within context.")
        if not self.committed:
            await self._transaction.rollback()

    async def commit(self):
        if self._transaction is None:
            raise UnitOfWorkError("commit() not called within context.")
        await self._transaction.commit()
        self.committed = True
