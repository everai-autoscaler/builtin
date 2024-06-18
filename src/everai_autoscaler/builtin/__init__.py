from .simple_autoscaler import SimpleAutoScaler
from .free_worker_autoscaler import FreeWorkerAutoScaler

from .builtin_manager import BuiltinManager

__all__ = [
    'SimpleAutoScaler',
    'FreeWorkerAutoScaler'
]

BuiltinManager().register(SimpleAutoScaler.autoscaler_name(), SimpleAutoScaler.from_arguments)
BuiltinManager().register(FreeWorkerAutoScaler.autoscaler_name(), FreeWorkerAutoScaler.from_arguments)
