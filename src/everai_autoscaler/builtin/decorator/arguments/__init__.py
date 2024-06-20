from everai_autoscaler.builtin.decorator.arguments.decorator import ArgumentsDecorator
from everai_autoscaler.builtin.decorator.arguments.noop import NoopDecorator
from everai_autoscaler.builtin.factory import Factory, Singleton


class ArgumentsFactory(Factory, metaclass=Singleton):
    ...


ArgumentsFactory().register(NoopDecorator.name(), NoopDecorator.from_arguments)


__all__ = [
    'ArgumentsDecorator',
    'ArgumentsFactory',
    'NoopDecorator',
]
