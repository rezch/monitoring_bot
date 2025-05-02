from collections.abc import Iterable
from typing import Generator


def is_pure_iterable(value) -> bool:
    """ is value is Iterable and not string or bytes """
    return isinstance(value, Iterable) and not (isinstance(value, str) or isinstance(value, bytes))


def flatten(data: list) -> Generator:
    """ flatten Iterable object for iteration """
    if not is_pure_iterable(data):
        yield data
        return

    for element in data:
        yield from flatten(element)


def optional_none(nullable_value, default):
    """
    return nullable_value if it's not None
    otherwise return default
    """
    return default if nullable_value is None else nullable_value
