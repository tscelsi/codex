from events.local import LocalPublisher, LocalSubscriber


class PrintSubscriber(LocalSubscriber):
    async def handle(self, event: dict[str, int]):
        print(event)


def test_publisher_init():
    p = LocalPublisher()
    assert p


def test_publisher_register():
    p = LocalPublisher()
    subscriber = PrintSubscriber(publisher=p)
    p.register(subscriber, "topic-1")
    assert subscriber in p.subscribers["topic-1"]


def test_publisher_publish_when_no_topic():
    p = LocalPublisher()
    try:
        p.publish({"payload": {"some-message": 1}})
    except ValueError as e:
        assert str(e) == "Event must have a topic"


def test_publisher_publish_when_no_subscriber():
    p = LocalPublisher()
    p.publish({"payload": {"some-message": 1}, "topic": "topic-1"})
    assert p._latest_event is not None  # type: ignore
    assert p._latest_event is not None  # type: ignore
