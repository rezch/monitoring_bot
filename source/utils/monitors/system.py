from enum import Enum
from typing import List, Dict
import psutil
import subprocess
import platform


class RESOURCE_TYPE(Enum):
    CPU = 0
    MEM = 1
    TIME = 2

    @staticmethod
    def to_str(res_type) -> str:
        result = {
            __class__.CPU: 'CPU',
            __class__.MEM: 'MEM',
            __class__.TIME: 'TIME'
        }
        return result[res_type]


def get_cpu_usage(percpu=False) -> int:
    """
    :return: cpu load (opt. per every core)
    """
    return psutil.cpu_percent(interval=1, percpu=percpu)


def get_cpu_avg_load() -> List[int]:
    """
    :return: avg cpu load over the last 1, 5 and 15 minutes
    """
    return psutil.getloadavg()


def get_memory_usage() -> dict:
    """
    :return: memory usage: ALL, USED, FREE, USED%
    """
    GB_SIZE = 1 << 30
    memory = psutil.virtual_memory()
    return {
        'ALL': f'{memory.total / GB_SIZE:.2f} Gb',
        'USED': f'{memory.used / GB_SIZE:.2f} Gb',
        'FREE': f'{memory.available / GB_SIZE:.2f} Gb',
        'USED %': f'{memory.percent}%'
    }


def get_memory_usage_raw():
    """
    :return: system memory usage
    """
    return psutil.virtual_memory()


def _parse_proc_info_linux(raw_info: str) -> Dict[str, str]:
    keys = [
        'PID', 'USER', 'PR', 'NI', 'VIRT', 'RES', 'SHR', 'S', 'CPU', 'MEM', 'TIME', 'COMMAND'
    ]

    all_info = dict(zip(keys, raw_info))

    return {
        'PID': all_info['PID'],
        'USER': all_info['USER'],
        'CPU': all_info['CPU'],
        'MEM': all_info['MEM'],
        'TIME': all_info['TIME'],
        'COMMAND': all_info['COMMAND']
    }


def _parse_proc_info_darwin(raw_info: str) -> Dict[str, str]:
    keys = [
        'CPU', 'TIME', '#TH', '#WQ', '#PORTS', 'MEM', 'PURG', 'CMPRS', 'PGRP', 'PPID', 'STATE', 'BOOSTS', '%CPU_ME', '%CPU_OTHRS', 'UID', 'FAULTS', 'COW', 'MSGSENT', 'MSGRECV', 'SYSBSD', 'SYSMACH', 'CSW', 'PAGEINS', 'IDLEW', 'POWER', 'INSTRS', 'CYCLES', 'JETPRI', 'USER', '#MREGS', 'RPRVT', 'VPRVT', 'VSIZE', 'KPRVT', 'KSHRD'
    ]

    # extract this params, because command name can have spaces
    base_info = {
        'PID': raw_info[:7].strip(),
        'COMMAND': raw_info[7:24].strip()
    }

    all_info = dict(
        zip(keys, list(filter(None, raw_info[24:].split(' '))))
    ) | base_info

    return {
        'PID': all_info['PID'],
        'USER': all_info['USER'],
        'CPU': all_info['CPU'],
        'MEM': all_info['MEM'],
        'TIME': all_info['TIME'],
        'COMMAND': all_info['COMMAND']
    }


def _get_top_processes_linux(count: int, sort_by: RESOURCE_TYPE) -> List[List[str]]:
    proc_info = subprocess.run(
        ["top", "-b", "-n", "1"],
        capture_output=True
        ).stdout \
        .decode('utf-8') \
        .split('\n') \
        [7:-1] # remove extra info

    return sorted(
        [_parse_proc_info_linux(list(filter(None, proc.split(' ')))) for proc in proc_info],
        key=lambda x: x[RESOURCE_TYPE.to_str(sort_by)],
        reverse=True
        )[:count]


def _get_top_processes_darwin(count: int, sort_by: RESOURCE_TYPE) -> List[List[str]]:
    # request 2 ps top to get more actual info
    proc_info = subprocess.run(
        ["top", "-l", "2"],
        capture_output=True
        ).stdout \
        .decode('utf-8') \
        .split('\n\n')[2] \
        .split('\n') \
        [1:-1] # remove extra info

    return sorted(
        [_parse_proc_info_darwin(proc) for proc in proc_info],
        key=lambda x: x[RESOURCE_TYPE.to_str(sort_by)],
        reverse=True
        )[:count]


def get_top_processes(count: int = 10, sort_by = RESOURCE_TYPE.CPU) -> List[List[str]]:
    """
    :param count: count of processes to return
    :param sort_by: resource to sort by
    :return: top processes by some resource usage
    """

    if platform.system() == 'Darwin':
        return _get_top_processes_darwin(count, sort_by)
    return _get_top_processes_linux(count, sort_by)
