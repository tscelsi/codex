import asyncio

import pytest

from events.local import LocalPublisher, LocalSubscriber

pytestmark = pytest.mark.asyncio(loop_scope="function")


class PrintSubscriber(LocalSubscriber):
    async def handle(self, event: dict[str, int]):
        print(event)


PubAndSubType = tuple[LocalPublisher, PrintSubscriber]


@pytest.fixture
def pub_and_sub() -> PubAndSubType:
    p = LocalPublisher()
    s = PrintSubscriber(publisher=p)
    return p, s


async def test_subcriber_receives_messages_in_queue(
    pub_and_sub: PubAndSubType,
):
    p = pub_and_sub[0]
    s = pub_and_sub[1]
    s.subscribe(["topic-1"])
    p.publish({"payload": {"some-message": 1}, "topic": "topic-1"})
    assert s.queue.get_nowait() == {
        "payload": {"some-message": 1},
        "topic": "topic-1",
    }


async def test_subscriber_handles_messages(pub_and_sub: PubAndSubType):
    p = pub_and_sub[0]
    s = pub_and_sub[1]
    s.subscribe(["topic-1"])
    p.publish({"payload": {"some-message": 1}, "topic": "topic-1"})
    event = s.queue.get_nowait()
    await s.handle(event)
    assert s.queue.empty()


async def test_subscriber_handles_message_while_listening(
    pub_and_sub: PubAndSubType,
):
    p = pub_and_sub[0]
    s = pub_and_sub[1]
    s.subscribe(["topic-1"])
    p.publish({"payload": {"some-message": 1}, "topic": "topic-1"})
    p.publish({"payload": {"some-message": 2}, "topic": "topic-1"})
    # subscriber shouldn't handle this third message as wrong topic
    p.publish({"payload": {"some-message": 2}, "topic": "topic-2"})
    await asyncio.sleep(0)
    assert s.queue.empty()
    assert s.num_handled == 2


async def test_subscriber_subscribe_is_idempotent(pub_and_sub: PubAndSubType):
    p = pub_and_sub[0]
    s = pub_and_sub[1]
    s.subscribe(["topic-1"])
    s.subscribe(["topic-1", "topic-2"])
    p.publish({"payload": {"some-message": 1}, "topic": "topic-1"})
    p.publish({"payload": {"some-message": 1}, "topic": "topic-2"})
    await asyncio.sleep(0)
    assert s.queue.empty()
    assert s.num_handled == 2
    assert s.num_handled == 2
    assert s.num_handled == 2


@pytest.mark.skip(reason="This test is slow")
async def test_heavy_workload_subscriber():
    class HeavySubscriber(LocalSubscriber):
        async def handle(self, event: dict[str, int]):
            await asyncio.sleep(0.1)
            print(event)

    p = LocalPublisher()
    s1 = HeavySubscriber(publisher=p)
    s2 = PrintSubscriber(publisher=p)
    s1.subscribe(["topic-1"])
    s2.subscribe(["topic-1"])
    for i in range(100):
        p.publish({"payload": {"some-message": i}, "topic": "topic-1"})
    assert s1.num_handled == 0
    assert s1.queue.qsize() == 100
    assert s2.num_handled == 0
    assert s2.queue.qsize() == 100
    await asyncio.sleep(1)
    assert s2.num_handled == 100
    assert s1.num_handled == 9
