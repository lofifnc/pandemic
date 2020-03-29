from enum import Enum
from typing import Iterable, Any


def iterable_to_string(iterable: Iterable[Enum]) -> str:
    return " ".join(map(lambda e: e.name, iterable))
