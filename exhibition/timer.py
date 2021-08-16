import asyncio
from exhibition.base import *
from exhibition.message import *


class Timer:
    def __init__(self, queue: asyncio.Queue, data: Message | ActionEnum, interval):
        self.queue = queue
        message = data if isinstance(data, Message) else Message(action=data)
        message.from_timer = True
        self.message = message
        self.interval = interval
        self.task: asyncio.Task = None
        self.join_event = asyncio.Event()
        self.loop = asyncio.get_event_loop()

    def start(self):
        if self.task:
            raise ValueError(f'已在定时')

        loop = self.loop
        async def timer():
            try:
                await asyncio.wait_for(self.join_event.wait(), self.interval)
            except asyncio.CancelledError:
                return
            except asyncio.TimeoutError:
                loop.call_soon_threadsafe(loop.create_task, self.queue.put(self.message))
        self.task = asyncio.create_task(timer())

    async def stop(self):
        if not self.task:
            raise ValueError(f'未定时')
        self.join_event.set()
        self.task.cancel()
        await self.task
        self.task = None
        self.clean()

    def clean(self):
        self.message = None
        self.queue = None
        self.loop = None


__all__ = [
    'Timer',
]
