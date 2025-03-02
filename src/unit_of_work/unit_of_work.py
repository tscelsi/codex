import abc

from databases import Database


class UnitOfWorkError(Exception):
    pass


class AbstractUnitOfWork(abc.ABC):
    async def __aexit__(self, exc_type: type, exc_val: Exception, exc_tb: object):
        await self.rollback()

    async def __aenter__(self) -> "AbstractUnitOfWork":
        return self

    @abc.abstractmethod
    async def commit(self):
        pass

    @abc.abstractmethod
    async def rollback(self):
        pass

    @abc.abstractmethod
    def register_new(self, entity: object):
        pass

    @abc.abstractmethod
    def register_deleted(self, entity: object):
        pass

    @abc.abstractmethod
    def register_dirty(self, entity: object):
        pass


class DatabasesUnitOfWork(AbstractUnitOfWork):
    def __init__(self, database: Database):
        self._database = database
        self._transaction = None
        self.committed = False

    async def __aenter__(self) -> AbstractUnitOfWork:
        self._transaction = await self._database.transaction()
        return await super().__aenter__()

    async def __aexit__(self, exc_type: type, exc_val: Exception, exc_tb: object):
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
