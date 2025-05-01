from collections.abc import Iterable
from typing import Any, Generator


def is_pure_iterable(value):
    return isinstance(value, Iterable) and not (isinstance(value, str) or isinstance(value, bytes))


def flatten(data: list) -> Generator:
    if not is_pure_iterable(data):
        yield data
        return

    for element in data:
        yield from flatten(element)


def optional_none(nullable_value: Any, default: Any):
    return default if nullable_value is None else nullable_value
