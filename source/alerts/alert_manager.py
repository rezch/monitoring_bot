from alerts.alert_config import load_config
from alerts.structs import SystemInfo
from alerts.handlers import AlertHandler
from config import PROXY_IP, LOG_PATH, LOG_CAPACITY
from utils.monitors.system import coro_get_cpu_usage, coro_get_memory_usage_raw
from utils.monitors.network import connection_check
from utils.coro import task_pool, task_pool_single_args

import asyncio
from datetime import datetime, timedelta
import logging
import logging.handlers
from os import path


async def prepare_sys_info() -> SystemInfo:
    info = await task_pool({
        coro_get_cpu_usage: [],
        coro_get_memory_usage_raw: [],
        connection_check: ["0.0.0.0"],
    })

    return SystemInfo(
        cpu_usage=info[0],
        mem_usage=info[1].percent,
        connected=info[2])


def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(path.join(LOG_PATH, 'system.log'), mode='a')
    formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    memory_handler = logging.handlers.MemoryHandler(
        LOG_CAPACITY,
        flushLevel=logging.ERROR,
        target=handler,
        flushOnClose=True)
    logger.addHandler(memory_handler)

    return logger


class AlertManager:
    SLEEP_TIME = 1 # secs

    def __init__(self):
        self.handlers = []
        self.logger = get_logger()

    def add_alert(self, handler: AlertHandler) -> None:
        self.handlers.append(handler)

    @staticmethod
    def get_remaining_sleeptime(elapsed_time):
        return max(
            timedelta(seconds=AlertManager.SLEEP_TIME) - elapsed_time,
            timedelta()
        ).total_seconds()

    async def run(self):
        while True:
            start_time = datetime.now()
            info = await prepare_sys_info()

            self.logger.info(
                f"CPU: {info.cpu_usage}   MEM: {info.mem_usage}   NET: {info.connected}")
            print(f"CPU: {info.cpu_usage}   MEM: {info.mem_usage}   NET: {info.connected}")

            await task_pool_single_args(
                [task.check for task in self.handlers],
                info)

            elapsed_time = datetime.now() - start_time
            await asyncio.sleep(AlertManager.get_remaining_sleeptime(elapsed_time))

    def load_config(self) -> None:
        for handler in load_config():
            self.handlers.append(handler)
