from utils.tools import is_pure_iterable

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


class Promise:
    def __init__(self):
        self.ready = False
        self.value = None
        self.event = asyncio.Event()

    def put(self, value):
        print("PUT: ", value)
        self.value = value
        self.event.set()

    async def get(self):
        await self.event.wait()
        return self.value


async def fetch_promise(promise, direct_order=False):
    """
    fetching value from promise, with waiting
    if given non promise value, just returns it
    if promise is iterable, iterates through it, and yields fetched values
    :param value: promise to value, or value
    :param direct_order: default=False, if True, yields values from iterable promise in direct order
    :return: fetched from promise value
    """
    if isinstance(promise, Promise):
        yield await promise.get()
        return
    if not is_pure_iterable(promise):
        yield promise
        return
    if direct_order:
        for value in promise:
            async for result in fetch_promise(value, True):
                yield result
    else:
        async for value in promise:
            async for result in fetch_promise(value):
                yield result


class TaskQueue:
    RUNNING = 0
    WAIT_TO_DIE = 1
    FORCE_DIE = 2

    class PackagedTask:
        def __init__(self, call, *args, **kwargs):
            self._call = call
            self._args = args
            self._kwargs = kwargs
            self.promise = Promise()

        async def call(self):
            if asyncio.iscoroutinefunction(self._call):
                return await self._call(*self._args, **self._kwargs)
            return self._call(*self._args, **self._kwargs)

    class QueueException(Exception):
        def __init__(self, message: str = None):
            self._message = optional_none(str, message)

        def __str__(self):
            return f"QuiteTaskQueue exception: {self._message}"

    def __init__(self, delay: float = 1, sleep_delay: float = 1, max_size: int = 10):
        self.delay = delay
        self.sleep_delay = sleep_delay
        self.max_size = max_size

        self.task_queue = []
        self.queue_lock = asyncio.Lock()
        self.state = TaskQueue.RUNNING
        self.run_loop = None
        self.max_size_call = lambda : ...

    def set_max_size_call(self, call):
        self.max_size_call = call

    async def join(self):
        self.state = TaskQueue.WAIT_TO_DIE
        if self.run_loop:
            await self.run_loop

    async def post(self, task: PackagedTask) -> Promise:
        if self.state != TaskQueue.RUNNING:
            raise TaskQueue.QueueException("attempt to post a call in the stopped queue.")
        async with self.queue_lock:
            if len(self.task_queue) > self.max_size:
                self.max_size_call()
                return
            self.task_queue.append(task)
        return self.task_queue[-1].promise

    def stop(self):
        self.state = TaskQueue.WAIT_TO_DIE

    def force_stop(self):
        self.state = TaskQueue.FORCE_DIE

    def run(self) -> Coroutine:
        # self.run_loop = asyncio.Task(self._run())
        self.run_loop = asyncio.gather(self._run())
        return self.run_loop

    def _check_queue(self):
        if self.task_queue:
            return True
        if self.state == TaskQueue.WAIT_TO_DIE:
            # task queue is empty, so TaskQueue can stop now
            self.state == TaskQueue.FORCE_DIE # TODO: ???
            return False
        return False

    async def _run(self):
        while self.state != TaskQueue.FORCE_DIE:
            task = None
            async with self.queue_lock:
                if self._check_queue():
                    task = self.task_queue.pop(0)

            if task is None:
                await asyncio.sleep(self.sleep_delay)
                continue

            task.promise.put(await task.call())
            await asyncio.sleep(self.delay)
