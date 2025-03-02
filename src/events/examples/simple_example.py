import asyncio
import logging

from events.local import LocalPublisher, LocalSubscriber

logging.basicConfig(level=logging.INFO)


class LogSubscriber(LocalSubscriber):
    async def handle(self, event: dict[str, str]):
        try:
            self._logger.info(f"{event['data']}")
        except KeyError:
            self._logger.error("Event must have a 'data' field")


async def main():
    p = LocalPublisher()
    s = LogSubscriber(publisher=p)
    # spawns new worker task handling incoming events
    s.subscribe(topics=["topic1"])

    p.publish({"topic": "topic1", "data": "hello"})
    p.publish({"topic": "topic1", "data": "world"})
    # won't log as subscriber is not subscribed to topic
    p.publish({"topic": "topic2", "data": "world"})
    # wait for tasks to complete in background
    await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
