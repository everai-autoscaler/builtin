import importlib
import typing
from everai_autoscaler.model import BuiltinAutoScaler


def is_builtin(obj: typing.Any) -> bool:
    if not isinstance(obj, BuiltinAutoScaler):
        return False

    obj_type = type(obj)
    obj_full_name = '.'.join([obj_type.__module__, obj_type.__name__])

    builtin_module = importlib.import_module("everai_autoscaler.builtin")
    for name in dir(builtin_module):
        attr = getattr(builtin_module, name)
        if not hasattr(attr, "__name__") or not hasattr(attr, "__module__"):
            continue

        attr_full_name = '.'.join([getattr(attr, '__module__'), getattr(attr, '__name__')])

        if attr_full_name == obj_full_name:
            return True

    return False
