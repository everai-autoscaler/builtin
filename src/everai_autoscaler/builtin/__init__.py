from .simple_autoscaler import SimpleAutoScaler
from .builtin_manager import BuiltinManager

__all__ = [
    'SimpleAutoScaler'
]

BuiltinManager().register(SimpleAutoScaler.autoscaler_name(), SimpleAutoScaler.from_arguments)
