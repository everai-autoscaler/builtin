from __future__ import annotations
import typing

from everai_autoscaler.model import Factors


class NoopDecorator:
    def __init__(self, *args, **kwargs) -> None:
        ...

    def __call__(self, factors: Factors) -> typing.Optional[Factors]:
        return factors

    @classmethod
    def name(cls) -> str:
        return 'noop'

    @classmethod
    def from_arguments(cls, arguments: typing.Dict[str, str]) -> NoopDecorator:
        return NoopDecorator(**arguments)
