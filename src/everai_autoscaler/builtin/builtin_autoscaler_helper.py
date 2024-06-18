import typing

from everai_autoscaler.model import ArgumentType


class BuiltinAutoscalerHelper:
    def get_argument_helper(self, name) -> ArgumentType:
        assert hasattr(self, name)
        prop = getattr(self, name)
        return prop

    def get_argument_value_helper(self, name: str) -> int:
        assert hasattr(self, name)
        prop = getattr(self, name)

        if callable(prop):
            return int(prop())
        elif isinstance(prop, int):
            return prop
        elif isinstance(prop, float):
            return int(prop)
        elif isinstance(prop, str):
            return int(prop)
        else:
            raise TypeError(f'Invalid argument type {type(prop)} for {name}')

    def get_arguments_value_helper(self, names: typing.List[str]) -> typing.Tuple[int, ...]:
        return tuple([self.get_argument_value_helper(x) for x in names])

    def autoscaler_arguments_helper(self, names: typing.List[str]) -> typing.Dict[str, ArgumentType]:
        return {k: v for k, v in zip(names, [self.get_argument_helper(n) for n in names])}
