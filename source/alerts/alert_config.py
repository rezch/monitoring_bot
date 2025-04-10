from alerts.handlers import \
    AlertHandler, AlertGroups, CpuAlertHandler, MemAlertHandler, ConnectionAlertHandler

from datetime import timedelta
from typing import Generator
import yaml


def prepare_check_delay(check_delay: str) -> timedelta:
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


def validate_max_usage(max_usage: float):
    if 0 >= max_usage or max_usage > 100:
        raise ValueError(f"Incorrect value for max usage: {max_usage}")


def load_handler(config) -> Generator:
    name = config['alert'].get('name', None)
    groups = AlertGroups[config['alert'].get('groups', 'ALL').upper()]
    check_delay = prepare_check_delay(config['alert'].get('chech-delay', '0 10 0'))

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


def load_config() -> Generator:
    with open("source/alerts/alert.yaml", "r") as file:
        config = yaml.safe_load(file)

    if 'monitorings' in config.keys():
        for handler in config['monitorings']:
            yield from load_handler(handler)
