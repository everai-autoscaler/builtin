from __future__ import annotations
import typing


class NoopDecorator:
    def __init__(self, *args, **kwargs) -> None:
        ...

    def __call__(self, arguments: typing.Dict[str, str]) -> typing.Dict[str, str]:
        return arguments

    @classmethod
    def name(cls) -> str:
        return 'noop'

    @classmethod
    def from_arguments(cls, arguments: typing.Dict[str, str]) -> NoopDecorator:
        return NoopDecorator(**arguments)
