import abc
import asyncio
import logging
import typing
from typing import Any
from uuid import uuid4

from utils.logger import CustomLoggingAdapter

Topic: typing.TypeAlias = str


class AbstractSubscriber(abc.ABC):
    def __init__(self) -> None:
        self._id = uuid4()
        self._worker: asyncio.Task[None] | None = None
        self._topics: set[Topic] = set()
        self._logger = CustomLoggingAdapter(
            logging.getLogger(__name__),
            {"ctx": self},
        )

    def __repr__(self):
        return f"sub-{self._id}"

    def _listening_task_done_callback(self, task: asyncio.Task[None]) -> None:
        """Callback for when the listening task is done.
        Only called when the task is cancelled, all other exceptions are
        handled in the _loop() fn."""
        self._logger.debug("loop done")
        self._listening_task = None
        try:
            exc = task.exception()
        except asyncio.CancelledError:
            exc = None
        if exc is not None:
            self._logger.error(f"Exited with exception: {exc}")
            self._logger.exception(exc)
            pass

    @abc.abstractmethod
    async def handle(self, event: dict[str, Any]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def subscribe(self, topics: list[str]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_message_loop(self) -> typing.NoReturn:
        """Loop that takes an item from the queue and handles it."""
        raise NotImplementedError
