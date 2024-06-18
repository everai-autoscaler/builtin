import typing

from everai_autoscaler.model import Factors


class NoopDecorator:
    def __init__(self):
        ...

    def __call__(self, factors: Factors) -> typing.Optional[Factors]:
        return factors
