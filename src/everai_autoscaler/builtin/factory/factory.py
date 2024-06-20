import typing
from .singleton import Singleton

T = typing.TypeVar('T')


class Factory(typing.Generic[T]):
    elements: typing.Dict[str, typing.Callable[[typing.Dict[str, str]], T]] = {}

    def __init__(self):
        self.elements = {}

    def register(self, name: str, creator: typing.Callable[[typing.Dict[str, str]], T]) -> None:
        self.elements[name] = creator

    def create(self, name: str, arguments: typing.Dict[str, str]) -> T:
        if name not in self.elements:
            raise ValueError(f'{name} not in factory, consider {self.elements.keys()}')
        return self.elements[name](arguments)

    def dump(self):
        print('available elements:')
        [print(name) for name in self.elements.keys()]
