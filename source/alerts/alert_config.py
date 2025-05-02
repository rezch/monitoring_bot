from .handlers import \
    AlertHandler, CpuAlertHandler, MemAlertHandler, ConnectionAlertHandler
from .structs import AlertGroups

from dataclasses import dataclass
from datetime import timedelta
from typing import Generator, List
import yaml


@dataclass
class Config:
    handlers: List[AlertHandler]
    check_delay: timedelta


def prepare_delay(check_delay: str) -> timedelta:
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


def validate_max_usage(max_usage: float) -> float:
    if 0 >= max_usage or max_usage > 100:
        raise ValueError(f"Incorrect value for max usage: {max_usage}")
    return max_usage


def load_handler(config) -> Generator:
    name = config['alert'].get('name', None)
    groups = AlertGroups[config['alert'].get('groups', 'ALL').upper()]
    check_delay = prepare_delay(config['alert'].get('check-delay', '0 10 0'))

    if 'cpu-max-usage' in config['alert'].keys():
        yield CpuAlertHandler(
            validate_max_usage(config['alert']['cpu-max-usage']),
            name,
            groups,
            check_delay)

    if 'mem-max-usage' in config['alert'].keys():
        yield MemAlertHandler(
            validate_max_usage(config['alert']['mem-max-usage']),
            name,
            groups,
            check_delay)

    if 'connection' in config['alert'].keys():
        yield ConnectionAlertHandler(name, groups, check_delay)

    return []


def load_config() -> Config:
    with open("source/alerts/alert.yaml", "r") as file:
        raw_config = yaml.safe_load(file)

    config = Config([], timedelta())
    if 'monitorings' in raw_config.keys():
        config.check_delay = prepare_delay(raw_config['monitorings']['check-delay'])
        for state in raw_config['monitorings']['alerts']:
            config.handlers += [handler for handler in load_handler(state)]

    return config
