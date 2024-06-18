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
    ArgumentType,
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

    def __init__(self,
                 min_workers: ArgumentType = 1,
                 max_workers: ArgumentType = 1,
                 min_free_workers: ArgumentType = 1,
                 max_idle_time: ArgumentType = 120,
                 scale_up_step: ArgumentType = 1):

        self.min_workers = min_workers if callable(min_workers) else int(min_workers)
        self.max_workers = max_workers if callable(max_workers) else int(max_workers)
        self.min_free_workers = min_free_workers if callable(min_free_workers) else int(min_free_workers)
        self.max_idle_time = max_idle_time if callable(max_idle_time) else int(max_idle_time)
        self.scale_up_step = scale_up_step if callable(scale_up_step) else int(scale_up_step)

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
        busy_count = 0

        # don't do scale up again
        in_flights = [worker for worker in factors.workers if worker.status == WorkerStatus.Inflight]
        if len(in_flights) > 0:
            return False

        free_workers_count = 0
        for worker in factors.workers:
            if worker.status == WorkerStatus.Free:
                free_workers_count += 1

        return free_workers_count < min_free_workers

    def decide(self, factors: Factors) -> DecideResult:
        assert factors.queue is not None

        min_workers, max_workers, min_free_workers, max_idle_time, scale_up_step = self.get_arguments()
        print(f'min_workers: {min_workers}, max_workers: {max_workers}, '
              f'min_free_workers: {min_free_workers}, max_idle_time: {max_idle_time}, scale_up_step: {scale_up_step}')

        now = int(datetime.now().timestamp())
        # scale up to min_workers
        if len(factors.workers) < min_workers:
            print(f'workers {len(factors.workers)} less than min_workers {min_workers}')
            return DecideResult(
                max_workers=max_workers,
                actions=[ScaleUpAction(count=min_workers - len(factors.workers))],
            )

        # ensure after scale down, satisfied the max_workers
        max_scale_up_count = max_workers - len(factors.workers)
        scale_up_count = 0
        if FreeWorkerAutoScaler.should_scale_up(factors, min_free_workers):
            scale_up_count = min(max_scale_up_count, scale_up_step)

        if scale_up_count > 0:
            return DecideResult(
                max_workers=max_workers,
                actions=[ScaleUpAction(count=scale_up_count)],
            )

        # check if scale down is necessary
        scale_down_actions = []
        factors.workers.sort(key=lambda x: x.started_at, reverse=True)
        for worker in factors.workers:
            if (worker.number_of_sessions == 0 and worker.status == WorkerStatus.Free and
                    now - worker.last_service_time >= max_idle_time):
                scale_down_actions.append(ScaleDownAction(worker_id=worker.worker_id))

        running_workers = 0
        for worker in factors.workers:
            if worker.status == WorkerStatus.Free:
                running_workers += 1

        # ensure after scale down, satisfied the min_workers
        max_scale_down_count = running_workers - min_workers
        scale_down_count = min(max_scale_down_count, len(scale_down_actions))
        return DecideResult(
            max_workers=max_workers,
            actions=scale_down_actions[:scale_down_count]
        )