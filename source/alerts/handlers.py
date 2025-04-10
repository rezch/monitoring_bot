import telegram

from dataclasses import dataclass, fields
from datetime import timedelta, datetime
from enum import Enum
from functools import partial


@dataclass
class SystemInfo:
    cpu_usage: int      # %
    mem_usage: int      # %
    connected: bool     # is there a connection to the proxy


class AlertGroups(Enum):
    ALL = 1
    CHANNEL = 2
    ADMINS = 3


def callback_logger_wrapper(get_callback):
    """ unused """
    def wrapper(*args, **kwargs):
        callback = get_callback(*args, **kwargs)
        def inner_wrapper(*args, **kwargs):
            print("LOG: ", *args)
            return callback(*args, **kwargs)
        return inner_wrapper
    return wrapper


def get_callback(groups: AlertGroups):
    if groups == AlertGroups.ALL:
        return telegram.report
    if groups == AlertGroups.CHANNEL:
        return partial(telegram.report, fallback=False)
    if groups == AlertGroups.ADMINS:
        return telegram.report_to_admins


class AlertHandler:
    def __init__(self,
                 name: str,
                 groups: AlertGroups,
                 chech_delay: timedelta):
        self.name = name
        self.callback = get_callback(groups)
        self.check_delay = chech_delay
        self.last_check = datetime.now() - timedelta(minutes=100)

    def check(self, info: SystemInfo) -> bool:
        return False

    def delayed(self) -> bool:
        if datetime.now() < self.last_check + self.check_delay:
            return True
        self.last_check = datetime.now()
        return False


class CpuAlertHandler(AlertHandler):
    def __init__(self,
                 max_usage: int,
                 name: str,
                 groups: AlertGroups,
                 chech_delay: timedelta):
        super().__init__(name, groups, chech_delay)
        self.max_usage = max_usage

    def check(self, info: SystemInfo) -> bool:
        if self.delayed() or info.cpu_usage < self.max_usage:
            return False
        self.callback(
            f"🟡 ALERT: {self.name}\nCPU usage overdraft {info.cpu_usage}\nExpected usage % < {self.max_usage}.")
        return True


class MemAlertHandler(AlertHandler):
    def __init__(self,
                 max_usage: int,
                 name: str,
                 groups: AlertGroups,
                 chech_delay: timedelta):
        super().__init__(name, groups, chech_delay)
        self.max_usage = max_usage

    def check(self, info: SystemInfo) -> bool:
        if self.delayed() or info.mem_usage < self.max_usage:
            return False
        self.callback(
            f"🟡 ALERT: {self.name}\nMemory usage overdraft {info.mem_usage}\nExpected usage % < {self.max_usage}.")
        return True


class ConnectionAlertHandler(AlertHandler):
    def __init__(self,
                 name: str,
                 groups: AlertGroups,
                 chech_delay: timedelta):
        super().__init__(name, groups, chech_delay)
        self.raised = False
        self.callback_messages = []

    def check(self, info: SystemInfo) -> None:
        if self.raised and info.connected:
            self.raised = False
            telegram.reply_to(
                f"🟢 FIXED: connection restored",
                self.callback_messages)

        if self.delayed() or info.connected:
            return False

        self.callback_messages = self.callback(
                f"🔴 CRIT: connection failed\nUnable to connect to the proxy server.")
