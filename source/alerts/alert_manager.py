from alerts.alert_config import load_config
from alerts.handlers import AlertHandler, SystemInfo
from config import PROXY_IP
from utils.monitors.system import get_cpu_usage, get_memory_usage_raw
from utils.monitors.network import connection_check

import asyncio
from datetime import timedelta
from typing import List, Dict
import yaml


def prepare_sys_info() -> SystemInfo:
    return SystemInfo(
        get_cpu_usage(),
        get_memory_usage_raw().percent,
        connection_check(PROXY_IP)
    )


class AlertManager:
    SLEEP_TIME = 1 # secs

    def __init__(self):
        self.handlers = []

    def add_alert(self, handler: AlertHandler) -> None:
        self.handlers.append(handler)

    async def run(self) -> None:
        while True:
            info = prepare_sys_info()

            for handler in self.handlers:
                handler.check(info)

            print(f"CPU: {info.cpu_usage}   MEM: {info.mem_usage}   NET: {info.connected}")

            await asyncio.sleep(AlertManager.SLEEP_TIME)

    def load_config(self) -> None:
        for handler in load_config():
            self.handlers.append(handler)
