import asyncio
from collections.abc import Callable
from typing import Coroutine, Dict, List
from .tools import optional_none


async def quite_task_pool(tasks: Callable, *args, **kwargs) -> None:
    async with asyncio.TaskGroup() as tg:
        for task in tasks:
            tg.create_task(task(*args, **kwargs))


async def task_pool_single_args(tasks: Callable, *args, **kwargs) -> List:
    async with asyncio.TaskGroup() as tg:
        promises = [
            tg.create_task(
                task(*args, **kwargs))
            for task in tasks
        ]

    return [await promise for promise in promises]


async def task_pool(packaged_tasks: Dict[Callable, List]):
    async with asyncio.TaskGroup() as tg:
        promises = [
            tg.create_task(
                task(*args))
            for task, args in packaged_tasks.items()
        ]

    return [await promise for promise in promises]


class QueueException(Exception):
    def __init__(self, message: str = None):
        self._message = optional_none(message)

    def __str__(self):
        return f"QuiteTaskQueue exception: {self._message}"


class Promise:
    def __init__(self):
        self.ready = False
        self.value = None
        self.cv = asyncio.Condition()

    def put(self, value):
        self.value = value
        self.cv.notify_all()

    async def get(self):
        async with self.cv:
            await self.cv.wait()
        return self.value


async def fetch_message(value):
    """
    fetching value from promise, with waiting
    if given non promise value, just returns it
    :param value: promise to value, or value
    :return: value (non promise)
    """
    if isinstance(value, Promise):
        return await value.get()
    return value


class TaskQueue:
    RUNNING = 0
    WAIT_TO_DIE = 1
    FORCE_DIE = 2

    def __init__(self, delay: float = 1, sleep_delay: float = 1):
        self.call_queue = []
        self.ctx_queue = []
        self.promise_queue = []
        self.delay = delay
        self.sleep_delay = sleep_delay
        self.state = TaskQueue.RUNNING
        self.run_loop = None

    async def join(self):
        self.state = TaskQueue.WAIT_TO_DIE
        if self.run_loop:
            await self.run_loop

    def post(self, call, *args, **kwargs) -> Promise:
        if self.state != TaskQueue.RUNNING:
            raise QueueException("attempt to post a call in the stopped queue.")
        print("POST:", call.__name__, args, kwargs)
        self.call_queue.append(call)
        self.ctx_queue.append((args, kwargs))
        promise = Promise()
        self.promise_queue.append(promise)
        return promise

    def stop(self):
        self.state = TaskQueue.WAIT_TO_DIE

    def force_stop(self):
        self.state = TaskQueue.FORCE_DIE

    def run(self) -> Coroutine:
        self.run_loop = self._run()
        return self.run_loop

    async def _run(self):
        while self.state != TaskQueue.FORCE_DIE:
            if not self.call_queue:
                if self.state == TaskQueue.WAIT_TO_DIE:
                    return
                await asyncio.sleep(self.sleep_delay)
                continue

            print("FETCH TASK")
            call, ctx, promise = [
                await x for x in map(
                    fetch_message,
                    (self.call_queue.pop(0),
                    *self.ctx_queue.pop(0),
                    self.promise_queue.pop(0)))]
            print(call, ctx, promise)

            promise.put(await call(*ctx))
            await asyncio.sleep(self.delay)
