import typing

from .simple_autoscaler import SimpleAutoScaler
from .free_worker_autoscaler import FreeWorkerAutoScaler
from everai_autoscaler.builtin.factory import Factory, Singleton
from everai_autoscaler.model import BuiltinAutoScaler

__version__ = "0.1.49"

T = typing.TypeVar('T', bound=BuiltinAutoScaler)


class BuiltinFactory(Factory, metaclass=Singleton):
    ...


BuiltinFactory().register(SimpleAutoScaler.autoscaler_name(), SimpleAutoScaler.from_arguments)
BuiltinFactory().register(FreeWorkerAutoScaler.autoscaler_name(), FreeWorkerAutoScaler.from_arguments)


__all__ = [
    'SimpleAutoScaler',
    'FreeWorkerAutoScaler',
    'BuiltinFactory',
    '__version__',
]



