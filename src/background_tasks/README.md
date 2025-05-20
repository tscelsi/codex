# Background Tasks

Simple wrapper around `asyncio.create_task` to schedule background tasks that don't interrupt the flow of the program. Useful for behaviour that is longer running and doesn't need to be awaited, such as sending messages to a queue, uploading a file to a remote server or logging.

The general flow of use is as follows:

```python
# assume there is an event loop running
from background_tasks import BackgroundTasks

taks_manager = BackgroundTasks()

async def some_coro():
    # Simulate a long-running upload task
    await asyncio.sleep(5)
    print("Done!")

tasks_manager.add(some_coro)  # runs in the background
print("Doing something else, like returning a response to a user")
await tasks_manager.wait()  # wait for all tasks to complete
```