from everai_autoscaler.builtin.decorator.factors.decorator import FactorsDecorator
from everai_autoscaler.builtin.decorator.factors.average import AverageDecorator
from everai_autoscaler.builtin.decorator.factors.noop import NoopDecorator
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

