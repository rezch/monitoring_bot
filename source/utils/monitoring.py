from enum import Enum
from typing import List, Dict
import psutil
import subprocess


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


def get_cpu_usage(percpu=False) -> List[int]:
    ''' return cpu load (opt. per every core)'''
    return psutil.cpu_percent(interval=1, percpu=percpu)


def get_cpu_avg_load() -> List[int]:
    ''' return avg cpu load over the last 1, 5 and 15 minutes '''
    return psutil.getloadavg()


def get_memory_usage() -> dict:
    ''' return memory usage: ALL, USED, FREE, USED% '''
    GB_SIZE = 1 << 30
    memory = psutil.virtual_memory()
    return {
        'ALL': f'{memory.total / GB_SIZE:.2f} Gb',
        'USED': f'{memory.used / GB_SIZE:.2f} Gb',
        'FREE': f'{memory.available / GB_SIZE:.2f} Gb',
        'USED %': f'{memory.percent}%'
    }


def _parse_proc_info(raw_info: str) -> Dict[str, str]:
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


def get_top_processes(count: int = 10, sort_by = RESOURCE_TYPE.CPU) -> List[List[str]]:
    ''' return top processes by processor usage '''

    proc_info = subprocess.run(
        ["top", "-b", "-n", "1"],   # get procceses info
        capture_output=True
        ).stdout \
        .decode('utf-8') \
        .split('\n') \
        [7:-1]          # remove extra info

    return sorted(
        [_parse_proc_info(list(filter(None, proc.split(' ')))) for proc in proc_info],
        key=lambda x: x[RESOURCE_TYPE.to_str(sort_by)],
        reverse=True
        )[:count]
