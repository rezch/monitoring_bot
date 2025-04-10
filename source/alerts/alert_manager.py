import logging.handlers
from alerts.alert_config import load_config
from alerts.handlers import AlertHandler, SystemInfo
from config import PROXY_IP, LOG_PATH, LOG_CAPACITY
from utils.monitors.system import get_cpu_usage, get_memory_usage_raw
from utils.monitors.network import connection_check

import asyncio
import logging
from os import path


def prepare_sys_info() -> SystemInfo:
    return SystemInfo(
        get_cpu_usage(),
        get_memory_usage_raw().percent,
        connection_check(PROXY_IP)
    )


def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(path.join(LOG_PATH, 'system.log'), mode='a')
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

    async def run(self) -> None:
        while True:
            info = prepare_sys_info()

            for handler in self.handlers:
                handler.check(info)

            self.logger.info(
                f"CPU: {info.cpu_usage}   MEM: {info.mem_usage}   NET: {info.connected}")

            await asyncio.sleep(AlertManager.SLEEP_TIME)

    def load_config(self) -> None:
        for handler in load_config():
            self.handlers.append(handler)
