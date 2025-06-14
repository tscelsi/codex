import asyncio
from typing import NoReturn

from redis.asyncio import Redis as AsyncRedis

from events.base import AbstractSubscriber


class LocalSubscriber(AbstractSubscriber):
    def __init__(self, r: AsyncRedis):
        self.r = r
        super().__init__()

    async def subscribe(self, topics: list[str]):
        """Subscribe to a topic.

        a) Register the subscriber with the broker
        b) Start the worker if it's not already running

        Args:
            topic (str): The topic to subscribe to
        """
        self._logger.debug(f"Subscribing to {topics}")
        async with self.r.pubsub() as pubsub:
            await pubsub.subscribe(*topics)
            self._topics.update(topics)
            self._logger.debug(f"Subscribed to {topics}")
        if self._worker is None:
            self._logger.debug("Starting worker coro")
            self._worker = asyncio.create_task(self.get_message_loop())
            self._worker.add_done_callback(self._listening_task_done_callback)

    async def get_message_loop(self) -> NoReturn:
        """Loop that takes an item from the queue and handles it."""
        self._logger.debug("loop started")
        async with self.r.pubsub() as pubsub:
            while True:
                event = await pubsub.get_message(
                    ignore_subscribe_messages=True
                )
                self._logger.debug(f"Received event: {event}")
                try:
                    if event:
                        self._logger.debug(f"Handling event: {event}")
                        await self.handle(event)
                except asyncio.CancelledError:
                    raise
                except BaseException as e:
                    self._logger.exception(e)
                finally:
                    self._logger.debug(f"Done handling event: {event}")
