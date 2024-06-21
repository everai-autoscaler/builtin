import typing

from everai_autoscaler.model import Factors

FactorsDecorator = typing.Callable[[Factors], typing.Optional[Factors]]
