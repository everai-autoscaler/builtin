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


class SimpleAutoScaler(BuiltinAutoScaler):
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

    def get_argument(self, name: str) -> int:
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

    def get_arguments(self) -> typing.Tuple[int, int, int, int, int]:
        min_workers = self.get_argument('min_workers')
        max_workers = self.get_argument('max_workers')
        max_queue_size = self.get_argument('max_queue_size')
        max_idle_time = self.get_argument('max_idle_time')
        scale_up_step = self.get_argument('scale_up_step')

        return min_workers, max_workers, max_queue_size, max_idle_time, scale_up_step

    @staticmethod
    def should_scale_up(factors: Factors, max_queue_size: int) -> bool:
        busy_count = 0

        # don't do scale up again
        in_flights = [worker for worker in factors.workers if worker.status == WorkerStatus.Inflight]
        if len(in_flights) > 0:
            return False

        busy_count = factors.queue.queue.get(QueueReason.QueueDueBusy) or 0
        # for req in factors.queue.requests:
        #     if req.queue_reason == QueueReason.QueueDueBusy:
        #         busy_count += 1
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

        # ensure after scale down, satisfied the max_workers
        max_scale_up_count = max_workers - len(factors.workers)
        scale_up_count = 0
        if SimpleAutoScaler.should_scale_up(factors, max_queue_size):
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
