from .decorator import FactorsDecorator
from .average import AverageDecorator
from .noop import NoopDecorator
from everai_autoscaler.builtin.factory import Factory, Singleton


class FactorsFactory(Factory, metaclass=Singleton):
    ...


FactorsFactory().register(NoopDecorator.name(), NoopDecorator.from_arguments)
FactorsFactory().register(AverageDecorator.name(), AverageDecorator.from_arguments)


__all__ = [
    'FactorsDecorator',
    'NoopDecorator',
    'AverageDecorator',
    'FactorsFactory',
]

