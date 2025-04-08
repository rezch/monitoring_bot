from config import PROXY_IP
import telegram
from utils.monitoring import get_cpu_usage, get_memory_usage_raw

import asyncio
from dataclasses import dataclass, fields
from datetime import timedelta, datetime
from typing import List, Dict
import subprocess
import yaml


@dataclass
class AlertConfig:
    name: str = ""

    # usage params
    cpu_max_load: int = None    # %
    mem_max_load: int = None    # %

    # delay between load checks
    # format in conf: HH MM SS
    check_delay: timedelta = timedelta(minutes=5)


class Alert:
    def __init__(self, conf = AlertConfig()):
        self.config = conf
        self.mute = None
        self.last_check = datetime.now() - timedelta(minutes=100)

    def mute(self, until: datetime) -> None:
        self.mute = until

    def process_mute(self) -> bool:
        if self.mute is None or datetime.now() > self.mute:
            self.mute = None
            return True
        return False

    def process_check(self) -> bool:
        if datetime.now() > self.last_check + self.config.check_delay:
            return True
        return False

    async def call(self, load_info: Dict) -> None:
        if not self.process_mute() or not self.process_check():
            return

        self.last_check = datetime.now()

        if self.config.cpu_max_load is not None and self.config.cpu_max_load < load_info['cpu_usage']:
            telegram.report(
                f"🟡 ALERT: {self.config.name}: cpu usage {load_info['cpu_usage']} > {self.config.cpu_max_load}")

        if self.config.mem_max_load is not None and self.config.mem_max_load < load_info['mem_usage']:
            telegram.report(
                f"🟡 ALERT: {self.config.name}: mem usage {load_info['mem_usage']} > {self.config.mem_max_load}")


def _prepare_check_delay(check_delay: str) -> timedelta:
    try:
        check_delay = list(map(int, check_delay.split(' ')))
    except:
        raise ValueError("Incorrect value for check_delay, use 'hh mm ss'")

    if len(check_delay) != 3:
        raise ValueError("Incorrect value for check_delay, use 'hh mm ss'")

    return timedelta(
        hours   = check_delay[0],
        minutes = check_delay[1],
        seconds = check_delay[2],
    )


class ConnectionAlert:
    CHECH_DELAY = timedelta(minutes=1)
    CONNECTION_TIMEOUT = 1 # sec

    def __init__(self):
        self.proxy_ip = PROXY_IP
        self.mute = None
        self.last_check = datetime.now() - timedelta(minutes=100)
        self.raised = False
        self.callback_messages = []

    def mute(self, until: datetime) -> None:
        self.mute = until

    def process_mute(self) -> bool:
        if self.mute is None or datetime.now() > self.mute:
            self.mute = None
            return True
        return False

    def process_check(self) -> bool:
        if datetime.now() > self.last_check + ConnectionAlert.CHECH_DELAY:
            return True
        return False

    def connection_check(self) -> bool:
        p = subprocess.Popen(['ping', '-c', '1', self.proxy_ip])
        try:
            p.wait(ConnectionAlert.CONNECTION_TIMEOUT)
            return True
        except subprocess.TimeoutExpired:
            p.kill()
        return False

    async def call(self, load_info: Dict) -> None:
        if not self.process_mute() or not self.process_check():
            return

        self.last_check = datetime.now()

        if raised := self.connection_check():
            self.callback_messages.append(telegram.report(
                f"🔴 CRIT: connection failed"))

        if self.raised != raised and raised == False:
            telegram.reply_to(
                self.callback_messages,
                f"🟢 FIXED: connection restored")
            self.callback_messages = []

        self.raised = raised


class AlertManager:
    SLEEP_TIME = 1 # secs

    def __init__(self):
        self.alerts: List[Alert] = []

    def add_alert(self, alert: Alert) -> None:
        self.alerts.append(alert)

    async def run(self) -> None:
        while True:
            load_info = {
                'cpu_usage': get_cpu_usage(),
                'mem_usage': get_memory_usage_raw().percent,
            }

            async with asyncio.TaskGroup() as tg:
                for alert in self.alerts:
                    tg.create_task(
                        alert.call(load_info))

            await asyncio.sleep(AlertManager.SLEEP_TIME)

    def load_config(self) -> None:
        with open("source/alerts/alert.yaml", "r") as file:
            config = yaml.safe_load(file)

        if 'monitorings' in config.keys():
            for alert in config['monitorings']:
                self.alerts.append(Alert(AlertConfig(
                    name=alert['alert']['name'],
                    cpu_max_load=int(alert['alert']['cpu-max-usage']),
                    mem_max_load=int(alert['alert']['mem-max-usage']),
                    check_delay=_prepare_check_delay(alert['alert']['check-delay']),
                )))
