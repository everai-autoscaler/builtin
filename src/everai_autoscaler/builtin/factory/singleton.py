from __future__ import annotations
import typing
from typing import (
    Generic
)

T = typing.TypeVar('T')


class Singleton(type, Generic[T]):
    _instances: dict[Singleton[T], T] = {}

    def __call__(cls, *args, **kwargs) -> T:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
