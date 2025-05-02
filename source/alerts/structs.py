from utils.coro import fetch_promise, TaskQueue

from dataclasses import dataclass
from enum import Enum


@dataclass
class SystemInfo:
    cpu_usage: int      # %
    mem_usage: int      # %
    connected: bool     # connection status


class AlertGroups(Enum):
    ALL = 1
    CHANNEL = 2
    ADMINS = 3


class PackagedMessage(TaskQueue.PackagedTask):
    def __init__(self, call, *args):
        """ kwargs are unsupported """
        super().__init__(call, args)

    @staticmethod
    async def fetch_args(args):
        unpacked_args = []
        async for arg in fetch_promise(args, direct_order=True):
            unpacked_args.append(arg)
        return unpacked_args

    async def call(self) -> None:
        self.promise.put(
            self._call(
                *await PackagedMessage.fetch_args(self._args)))
