from .decorator import ArgumentsDecorator
from .noop import NoopDecorator
from .time_match import TimeMatchDecorator
from everai_autoscaler.builtin.factory import Factory, Singleton


class ArgumentsFactory(Factory, metaclass=Singleton):
    ...


ArgumentsFactory().register(NoopDecorator.name(), NoopDecorator.from_arguments)
ArgumentsFactory().register(TimeMatchDecorator.name(), TimeMatchDecorator.from_arguments)


__all__ = [
    'ArgumentsDecorator',
    'ArgumentsFactory',
    'NoopDecorator',
    'TimeMatchDecorator',
]
