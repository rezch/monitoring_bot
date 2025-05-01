from utils.coro import fetch_promise, TaskQueue

from dataclasses import dataclass
from enum import Enum


@dataclass
class SystemInfo:
    cpu_usage: int      # %
    mem_usage: int      # %
    connected: bool     # is there a connection to the proxy


class AlertGroups(Enum):
    ALL = 1
    CHANNEL = 2
    ADMINS = 3


class PackagedMessage(TaskQueue.PackagedTask):
    def __init__(self, call, *args):
        """ kwargs are unsupported """
        super().__init__(call, args)

    async def call(self):
        unpacked_args = []
        async for arg in fetch_promise(self._args, direct_order=True):
            unpacked_args.append(arg)
        return self._call(*unpacked_args)
