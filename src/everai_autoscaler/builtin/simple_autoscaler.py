from __future__ import annotations
from datetime import datetime

import typing

from everai_autoscaler.model import (
    BuiltinAutoScaler,
    Factors,
    QueueReason,
    WorkerStatus,
    ScaleUpAction,
    ScaleDownAction,
    DecideResult,
    ArgumentType,
)

from .builtin_autoscaler_helper import BuiltinAutoscalerHelper


class SimpleAutoScaler(BuiltinAutoScaler, BuiltinAutoscalerHelper):
    # The minimum number of worker, even all of those are idle
    min_workers: ArgumentType
    # The maximum number of worker, even there are some request in queued_request.py
    max_workers: ArgumentType
    # The max_queue_size let scheduler know it's time to scale up
    max_queue_size: ArgumentType
    # The quantity of each scale up
    scale_up_step: ArgumentType
    # The max_idle_time in seconds let scheduler witch worker should be scale down
    max_idle_time: ArgumentType

    def __init__(self,
                 min_workers: ArgumentType = 1,
                 max_workers: ArgumentType = 1,
                 max_queue_size: ArgumentType = 1,
                 max_idle_time: ArgumentType = 120,
                 scale_up_step: ArgumentType = 1):

        self.min_workers = min_workers if callable(min_workers) else int(min_workers)
        self.max_workers = max_workers if callable(max_workers) else int(max_workers)
        self.max_queue_size = max_queue_size if callable(max_queue_size) else int(max_queue_size)
        self.max_idle_time = max_idle_time if callable(max_idle_time) else int(max_idle_time)
        self.scale_up_step = scale_up_step if callable(scale_up_step) else int(scale_up_step)

    @classmethod
    def scheduler_name(cls) -> str:
        return 'queue'

    @classmethod
    def autoscaler_name(cls) -> str:
        return 'simple'

    @classmethod
    def from_arguments(cls, arguments: typing.Dict[str, str]) -> SimpleAutoScaler:
        return SimpleAutoScaler(**arguments)

    def autoscaler_arguments(self) -> typing.Dict[str, ArgumentType]:
        return self.autoscaler_arguments_helper(
            [
                'min_workers', 'max_workers', 'max_queue_size', 'max_idle_time', 'scale_up_step'
            ]
        )

    def get_arguments(self) -> typing.Tuple[int, int, int, int, int]:
        result = self.get_arguments_value_helper([
            'min_workers', 'max_workers', 'max_queue_size', 'max_idle_time', 'scale_up_step'
        ])
        return result[0], result[1], result[2], result[3], result[4]

    @staticmethod
    def should_scale_up(factors: Factors, max_queue_size: int) -> bool:
        busy_count = 0

        # don't do scale up again
        in_flights = [worker for worker in factors.workers if worker.status == WorkerStatus.Inflight]
        if len(in_flights) > 0:
            return False

        busy_count = factors.queue.get(QueueReason.QueueDueBusy, None) or 0
        return busy_count > max_queue_size

    def decide(self, factors: Factors) -> DecideResult:
        assert factors.queue is not None

        min_workers, max_workers, max_queue_size, max_idle_time, scale_up_step = self.get_arguments()
        print(f'min_workers: {min_workers}, max_workers: {max_workers}, '
              f'max_queue_size: {max_queue_size}, max_idle_time: {max_idle_time}, scale_up_step: {scale_up_step}')

        now = int(datetime.now().timestamp())
        # scale up to min_workers
        if len(factors.workers) < min_workers:
            print(f'workers {len(factors.workers)} less than min_workers {min_workers}')
            return DecideResult(
                max_workers=max_workers,
                actions=[ScaleUpAction(count=min_workers - len(factors.workers))],
            )

        # ensure after scale up, satisfied the max_workers
        max_scale_up_count = max_workers - len(factors.workers)
        scale_up_count = 0
        if SimpleAutoScaler.should_scale_up(factors, max_queue_size):
            scale_up_count = min(max_scale_up_count, scale_up_step)

        if scale_up_count > 0:
            return DecideResult(
                max_workers=max_workers,
                actions=[ScaleUpAction(count=scale_up_count)],
            )

        return self.idle_time_scaledown_helper(
            factors=factors,
            min_workers=min_workers,
            max_workers=max_workers,
            max_idle_time=max_idle_time,
        )
