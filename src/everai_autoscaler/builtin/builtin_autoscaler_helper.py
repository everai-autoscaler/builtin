import typing
from datetime import datetime

from everai_autoscaler.model import ArgumentType, Factors, WorkerStatus, ScaleDownAction, DecideResult, ScaleUpAction


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

    @classmethod
    def general_scale_up_helper(cls,
                                factors: Factors,
                                min_workers: int,
                                max_workers: int,
                                scale_up_step: int,
                                key_argument: int
                                ) -> typing.Optional[DecideResult]:
        if factors is None:
            return DecideResult(
                max_workers=max_workers,
                actions=[],
            )
        now = int(datetime.now().timestamp())
        # scale up to min_workers
        if len(factors.workers) < min_workers:
            print(f'workers {len(factors.workers)} less than min_workers {min_workers}')
            return DecideResult(
                max_workers=max_workers,
                actions=[ScaleUpAction(count=min_workers - len(factors.workers))],
            )

        max_scale_up_count = max_workers - len(factors.workers)
        scale_up_count = 0
        assert hasattr(cls, 'should_scale_up')
        should_scale_up = getattr(cls, 'should_scale_up')
        assert callable(should_scale_up)

        if should_scale_up(factors, key_argument):
            scale_up_count = min(max_scale_up_count, scale_up_step)

        if scale_up_count > 0:
            return DecideResult(
                max_workers=max_workers,
                actions=[ScaleUpAction(count=scale_up_count)],
            )
        return None

    @classmethod
    def idle_time_scaledown_helper(
            cls,
            factors: Factors,
            min_workers: int,
            max_workers: int,
            max_idle_time: int) -> DecideResult:
        now = int(datetime.now().timestamp())
        # check if scale down is necessary
        scale_down_actions = []
        factors.workers.sort(key=lambda x: x.started_at, reverse=True)
        for worker in factors.workers:
            if (worker.number_of_sessions == 0 and worker.status == WorkerStatus.Free and
                    worker.current_request == 0 and
                    now - worker.last_service_time >= max_idle_time):
                scale_down_actions.append(ScaleDownAction(worker_id=worker.worker_id))

        running_workers = 0
        for worker in factors.workers:
            if worker.status == WorkerStatus.Free or worker.status == WorkerStatus.Busy:
                running_workers += 1

        # ensure after scale down, satisfied the min_workers
        max_scale_down_count = running_workers - min_workers
        scale_down_count = min(max_scale_down_count, len(scale_down_actions))
        return DecideResult(
            max_workers=max_workers,
            actions=scale_down_actions[:scale_down_count]
        )
