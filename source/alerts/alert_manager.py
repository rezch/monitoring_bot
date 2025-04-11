import logging.handlers
from alerts.alert_config import load_config
from alerts.handlers import AlertHandler, SystemInfo
from config import PROXY_IP, LOG_PATH, LOG_CAPACITY
from utils.monitors.system import coro_get_cpu_usage, coro_get_memory_usage_raw
from utils.monitors.network import connection_check

import asyncio
from datetime import datetime, timedelta
import logging
from os import path


async def prepare_sys_info() -> SystemInfo:
    tasks = []

    async with asyncio.TaskGroup() as tg:
        tasks = [
            tg.create_task(coro_get_cpu_usage()),
            tg.create_task(coro_get_memory_usage_raw()),
            tg.create_task(connection_check(PROXY_IP))]

    tasks = [task.result() for task in tasks]

    return SystemInfo(
        tasks[0],
        tasks[1].percent,
        tasks[2]
    )


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
    SLEEP_TIME = 0 # secs

    def __init__(self):
        self.handlers = []
        self.logger = get_logger()

    def add_alert(self, handler: AlertHandler) -> None:
        self.handlers.append(handler)

    @staticmethod
    def get_remaining_sleeptime(elapsed_time):
        return max(
            timedelta(seconds=AlertManager.SLEEP_TIME) - elapsed_time,
            timedelta(seconds=0)).total_seconds()

    async def run(self) -> None:
        while True:
            start_time = datetime.now()
            info = await prepare_sys_info()

            for handler in self.handlers:
                handler.check(info)

            self.logger.info(
                f"CPU: {info.cpu_usage}   MEM: {info.mem_usage}   NET: {info.connected}")

            elapsed_time = datetime.now() - start_time

            await asyncio.sleep(AlertManager.get_remaining_sleeptime(elapsed_time))

    def load_config(self) -> None:
        for handler in load_config():
            self.handlers.append(handler)
