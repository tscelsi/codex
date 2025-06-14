import abc


class UnitOfWorkError(Exception):
    pass


class AbstractUnitOfWork(abc.ABC):
    async def __aenter__(
        self, isolation: str | None = None
    ) -> "AbstractUnitOfWork":
        return self

    async def __aexit__(
        self, exc_type: type, exc_val: Exception, exc_tb: object
    ):
        await self.rollback()

    @abc.abstractmethod
    async def commit(self):
        pass

    @abc.abstractmethod
    async def rollback(self):
        pass
