from __future__ import annotations
from datetime import datetime
from .builtin_autoscaler_helper import BuiltinAutoscalerHelper
import typing

from everai_autoscaler.model import (
    BuiltinAutoScaler,
    Factors,
    QueueReason,
    WorkerStatus,
    ScaleUpAction,
    ScaleDownAction,
    DecideResult,
    ArgumentType, Decorators,
)


class FreeWorkerAutoScaler(BuiltinAutoScaler, BuiltinAutoscalerHelper):
    # The minimum number of worker, even all of those are idle
    min_workers: ArgumentType
    # The maximum number of worker, even there are some request in queued_request.py
    max_workers: ArgumentType
    # The min free workers let scheduler know it's time to scale up
    min_free_workers: ArgumentType
    # The quantity of each scale up
    scale_up_step: ArgumentType
    # The max_idle_time in seconds let scheduler witch worker should be scale down
    max_idle_time: ArgumentType

    decorators: typing.Optional[Decorators]

    def __init__(self,
                 min_workers: ArgumentType = 1,
                 max_workers: ArgumentType = 1,
                 min_free_workers: ArgumentType = 1,
                 max_idle_time: ArgumentType = 120,
                 scale_up_step: ArgumentType = 1,
                 decorators: typing.Optional[Decorators] = None,
                 ):
        self.min_workers = min_workers if callable(min_workers) else int(min_workers)
        self.max_workers = max_workers if callable(max_workers) else int(max_workers)
        self.min_free_workers = min_free_workers if callable(min_free_workers) else int(min_free_workers)
        self.max_idle_time = max_idle_time if callable(max_idle_time) else int(max_idle_time)
        self.scale_up_step = scale_up_step if callable(scale_up_step) else int(scale_up_step)
        self.decorators = decorators

    @classmethod
    def scheduler_name(cls) -> str:
        return 'queue'

    @classmethod
    def autoscaler_name(cls) -> str:
        return 'free-worker'

    @classmethod
    def from_arguments(cls, arguments: typing.Dict[str, str]) -> FreeWorkerAutoScaler:
        return FreeWorkerAutoScaler(**arguments)

    def autoscaler_arguments(self) -> typing.Dict[str, ArgumentType]:
        return self.autoscaler_arguments_helper(
            [
                'min_workers', 'max_workers', 'min_free_workers', 'max_idle_time', 'scale_up_step'
            ]
        )

    def get_arguments(self) -> typing.Tuple[int, int, int, int, int]:
        result = self.get_arguments_value_helper([
            'min_workers', 'max_workers', 'min_free_workers', 'max_idle_time', 'scale_up_step'
        ])
        return result[0], result[1], result[2], result[3], result[4]

    @staticmethod
    def should_scale_up(factors: Factors, min_free_workers: int) -> bool:
        workers = factors.workers or []

        if factors is None or factors.worker is None:
            return False

        # don't do scale up again
        in_flights = [worker for worker in workers if worker.status == WorkerStatus.Inflight]
        if len(in_flights) > 0:
            return False

        free_workers_count = factors.worker.get(WorkerStatus.Free, None) or 0

        return free_workers_count < min_free_workers

    def decide(self, factors: Factors) -> DecideResult:
        min_workers, max_workers, min_free_workers, max_idle_time, scale_up_step = self.get_arguments()
        print(f'min_workers: {min_workers}, max_workers: {max_workers}, '
              f'min_free_workers: {min_free_workers}, max_idle_time: {max_idle_time}, scale_up_step: {scale_up_step}')

        result = FreeWorkerAutoScaler.general_scale_up_helper(
            factors=factors, min_workers=min_workers, max_workers=max_workers, scale_up_step=scale_up_step,
            key_argument=min_free_workers,
        )
        if result:
            return result

        return self.idle_time_scaledown_helper(
            factors=factors,
            min_workers=min_workers,
            max_workers=max_workers,
            max_idle_time=max_idle_time,
        )
