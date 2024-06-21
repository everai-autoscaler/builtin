from __future__ import annotations
import typing

from everai_autoscaler.model import Factors, Queue, QueueReason


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
        self.used_histories = int(used_histories)

    @classmethod
    def name(cls) -> str:
        return 'average'

    @classmethod
    def from_arguments(cls, arguments: typing.Dict[str, str]) -> AverageDecorator:
        return AverageDecorator(**arguments)

    def __call__(self, factors: Factors) -> typing.Optional[Factors]:
        if factors is None:
            return None

        if len(factors.queue_histories) < self.used_histories:
            return None

        result_queue = {
            QueueReason.NotDispatch: 0,
            QueueReason.QueueDueBusy: 0,
            QueueReason.QueueDueSession: 0,
        }
        result_queue.update(factors.queue)

        used = 0
        for _, h in sorted(factors.queue_histories.items(), key=lambda item: item[0]):
            for reason, count in h.items():
                result_queue[reason] += count
            used += 1
            if used >= self.used_histories:
                break

        result_queue[QueueReason.NotDispatch] = int(result_queue[QueueReason.NotDispatch] / (self.used_histories + 1))
        result_queue[QueueReason.QueueDueBusy] = int(result_queue[QueueReason.QueueDueBusy] / (self.used_histories + 1))
        result_queue[QueueReason.QueueDueSession] = int(result_queue[QueueReason.QueueDueSession] / (self.used_histories + 1))
        return Factors(
            queue_histories=factors.queue_histories,
            queue=result_queue,
            utilization=factors.utilization,
            workers=factors.workers,
        )
