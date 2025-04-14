from alerts.structs import SystemInfo
from config import STAT_IMAGE_PATH
from stats.log_fetcher import fetch_log
from stats.plot import make_basic_plot, make_basic_scatter_with_outliers

from datetime import timedelta
from matplotlib import pyplot as plt
from typing import List
from uuid import uuid4


class Stat:
    description: str = None

    @staticmethod
    def pull_data(sys_info: SystemInfo): return None

    @classmethod
    def make_plot(cls, data: List[SystemInfo], filename: str): return None


class CpuStat(Stat):
    description = "CPU usage % statistics"

    @staticmethod
    def pull_data(sys_info: SystemInfo) -> float:
        return sys_info.cpu_usage

    @classmethod
    def make_plot(cls, data: List[SystemInfo], filename: str):
        x = list(range(len(data)))
        y = [cls.pull_data(value) for value in data]

        plot = make_basic_plot(x, y)
        plot.set_ylim([0, 100])

        plt.savefig(filename)


class MemStat(Stat):
    description = "Memory usage % statistics"

    @staticmethod
    def pull_data(sys_info: SystemInfo) -> float:
        return sys_info.mem_usage

    @classmethod
    def make_plot(cls, data: List[SystemInfo], filename: str):
        x = list(range(len(data)))
        y = [cls.pull_data(value) for value in data]

        plot = make_basic_plot(x, y)
        plot.set_ylim([0, 100])

        plt.savefig(filename)


class NetStat(Stat):
    description = "Network fails statistics"

    @staticmethod
    def pull_data(sys_info: SystemInfo) -> bool:
        return sys_info.connected

    @classmethod
    def make_plot(cls, data: List[SystemInfo], filename: str):
        x = list(range(len(data)))
        y = [cls.pull_data(value) == False for value in data]

        plot = make_basic_scatter_with_outliers(x, y, lambda y: y == True)
        plot.set_ylim([0, 1.5])

        plt.savefig(filename)


def prepare_stat_image(period: timedelta, resource: Stat) -> str:
    """
    prepare a statictics image from the system usage logs

    :param period: for which period the statistics will be collected.
    :param period: resource type: CPU/MEM
    :return: uuid name of statistic image file
    """
    filename = f'{STAT_IMAGE_PATH}/{str(uuid4())}.png'

    # TODO: check existans of save dir

    sys_info = fetch_log(period)
    resource.make_plot(sys_info, filename)

    return filename
