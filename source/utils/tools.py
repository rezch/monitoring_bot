from collections.abc import Iterable
from typing import Generator


def is_pure_iterable(value):
    return isinstance(value, Iterable) and not (isinstance(value, str) or isinstance(value, bytes))


def flatten(data: list) -> Generator:
    if not is_pure_iterable(data):
        yield data
        return

    for element in data:
        if is_pure_iterable(element):
            yield from flatten(element)
        else:
            yield element
