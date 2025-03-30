from collections.abc import Iterable
from typing import Generator


def flatten(data: list) -> Generator:
    for x in data:
        if isinstance(x, Iterable) and not (isinstance(x, str) or isinstance(x, bytes)):
            yield from flatten(x)
        else:
            yield x
