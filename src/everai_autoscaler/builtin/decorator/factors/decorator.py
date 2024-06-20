import typing

from everai_autoscaler.model import Factors

FactorsDecorator = typing.Callable[[Factors], typing.Optional[Factors]]

ArgumentsDecorator = typing.Callable[[typing.Dict[str, str]], typing.Dict[str, str]]
