import typing

from everai_autoscaler.model import AutoScaler, BuiltinAutoScaler
from .singleton import Singleton


class BuiltinManager(metaclass=Singleton):
    builtins: typing.Dict[str, typing.Callable[[typing.Dict[str, str]], BuiltinAutoScaler]] = {}

    def register(self, name: str, creator: typing.Callable[[typing.Dict[str, str]], BuiltinAutoScaler]) -> None:
        self.builtins[name] = creator

    def __init__(self):
        self.builtins = {}

    def create_autoscaler(self, name: str, arguments: typing.Dict[str, str]) -> BuiltinAutoScaler:
        if name not in self.builtins:
            raise ValueError(f'no such builtin autoscaler: {name}, valid autoscaler: {self.builtins.keys()}')
        return self.builtins[name](arguments)

    def dump(self):
        print('available builtin autoscaler:')
        [print(name) for name in self.builtins.keys()]
