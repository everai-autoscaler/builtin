from __future__ import annotations
import typing

from everai_autoscaler.model import Factors, QueueReason, WorkerStatus


class AverageDecorator:
    """
    AverageDecorator is a factors decorator
    """
    used_histories: int

    def __init__(self, used_histories: int = 5):
        """
        :param used_histories:
        how many historical data will be used, if there is insufficient quantity in the queue_histories,
        it will return None, and AutoScaler will ignore this decision
        """
        assert used_histories >= 0
        self.used_histories = int(used_histories)

    @classmethod
    def name(cls) -> str:
        return 'average'

    @classmethod
    def from_arguments(cls, arguments: typing.Dict[str, str]) -> AverageDecorator:
        return AverageDecorator(**arguments)

    def _average_queue(self, factors: Factors) -> Factors:
        queue_histories = factors.queue_histories or []
        if len(queue_histories) < self.used_histories:
            result_queue =  None
        else:
            result_queue = {
                QueueReason.NotDispatch: 0,
                QueueReason.QueueDueBusy: 0,
                QueueReason.QueueDueSession: 0,
            }
            result_queue.update(factors.queue or {})

            used = 0
            for _, h in sorted(queue_histories.items(), key=lambda item: item[0]):
                for reason, count in h.items():
                    result_queue[reason] += count
                used += 1
                if used >= self.used_histories:
                    break

            result_queue[QueueReason.NotDispatch] = int(result_queue[QueueReason.NotDispatch] / (self.used_histories + 1))
            result_queue[QueueReason.QueueDueBusy] = int(result_queue[QueueReason.QueueDueBusy] / (self.used_histories + 1))
            result_queue[QueueReason.QueueDueSession] = int(
                result_queue[QueueReason.QueueDueSession] / (self.used_histories + 1))
        return Factors(
            queue_histories=factors.queue_histories,
            queue=result_queue,
            workers=factors.workers,
            worker=factors.worker,
            worker_histories=factors.worker_histories,
            utilization=factors.utilization,
        )

    def _average_workers(self, factors: Factors) -> typing.Optional[Factors]:
        worker_histories = factors.worker_histories or []

        inflight_exists = False
        if factors.worker and factors.worker.get(WorkerStatus.Inflight, 0) > 0:
            inflight_exists = True

        if len(worker_histories) < self.used_histories:
            result_worker = None
        else:
            result_worker = {
                WorkerStatus.Inflight: 0,
                WorkerStatus.Free: 0,
                WorkerStatus.Busy: 0,
            }
            result_worker.update(factors.worker or {})

            used = 0
            for _, h in sorted(worker_histories.items(), key=lambda item: item[0]):
                for status, count in h.items():
                    result_worker[status] += count
                used += 1
                if used >= self.used_histories:
                    break

            result_worker[WorkerStatus.Inflight] = int(
                result_worker[WorkerStatus.Inflight] / (self.used_histories + 1))
            result_worker[WorkerStatus.Free] = int(
                result_worker[WorkerStatus.Free] / (self.used_histories + 1))
            result_worker[WorkerStatus.Busy] = int(
                result_worker[WorkerStatus.Busy] / (self.used_histories + 1))

            # ensure inflight don't be forgot
            if inflight_exists and result_worker[WorkerStatus.Inflight] == 0:
                result_worker[WorkerStatus.Inflight] = 1

        return Factors(
            queue_histories=factors.queue_histories,
            queue=factors.queue,
            workers=factors.workers,
            worker=result_worker,
            worker_histories=factors.worker_histories,
            utilization=factors.utilization,
        )

    def __call__(self, factors: Factors) -> typing.Optional[Factors]:
        if factors is None:
            return None

        _averaged = self._average_workers(self._average_queue(factors))
        return _averaged

