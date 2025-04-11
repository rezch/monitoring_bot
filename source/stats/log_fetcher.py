from alerts.handlers import SystemInfo
from config import LOG_PATH

from datetime import datetime, timedelta
from typing import List
import os
from uuid import uuid4


def read_log(period: timedelta) -> List[str]:
    since = str((datetime.now() - period).replace(microsecond=0))
    since = '2025-04-11 18:01:00'

    with open(os.path.join(LOG_PATH, 'system.log'), 'r') as file:
        query = f'alerts.alert_manager {since}'

        buf_size = 128
        segment = None
        offset = 0
        file.seek(0, os.SEEK_END)
        file_size = remaining_size = file.tell()
        readed_lines = []

        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            file.seek(file_size - offset)
            buffer = file.read(min(remaining_size, buf_size))

            if remaining_size == file_size and buffer[-1] == ord('\n'):
                buffer = buffer[:-1]

            remaining_size -= buf_size
            lines = buffer.split('\n')

            if segment is not None:
                lines[-1] += segment

            segment = lines[0]
            lines = lines[1:]

            for line in reversed(lines):
                readed_lines.append(line)

            if readed_lines[-1] < query:
                break

        if segment is not None:
            lines.append(segment)

    if readed_lines[0] == '':
        readed_lines = readed_lines[1:]

    return readed_lines


def log_to_sysinfo(log) -> SystemInfo:
    try:
        log = log.split('   ')

        log = [value.split(': ')[1] for value in log]

        return SystemInfo(
            float(log[0]),
            float(log[1]),
            log[2] == "True"
        )
    except:
        return None


def convert_logs_to_info(logs: List[str]) -> List[SystemInfo]:
    result = []

    for info in logs:
        info = info.split('INFO')
        if len(info) < 2:
            continue

        info = log_to_sysinfo(info[1].strip())
        
        if info is not None:
            result.append(info)

    return result


def fetch_log(period: timedelta) -> List[SystemInfo]:
    """
    :param period: for which period the statistics will be collected.
    :return: fetched from logs systeminfo
    """
    return convert_logs_to_info(read_log(period))
