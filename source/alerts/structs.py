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
