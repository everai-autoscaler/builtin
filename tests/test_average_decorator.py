import unittest

from everai_autoscaler.model import Factors, QueueReason, WorkerStatus

from everai_autoscaler.builtin.decorator.factors import AverageDecorator


class TestDecorator(unittest.TestCase):
    def test_empty_history(self):
        factors = Factors(
            queue={
                QueueReason.QueueDueBusy: 0,
                QueueReason.QueueDueSession: 0,
                QueueReason.NotDispatch: 0,
            }
        )
        d = AverageDecorator()
        result = d(factors)
        self.assertIsNone(result.queue)

    def test_not_enough(self):
        factors = Factors(
            queue_histories={
                10: {
                    QueueReason.QueueDueBusy: 0,
                    QueueReason.QueueDueSession: 0,
                    QueueReason.NotDispatch: 0,
                },
                20: {
                    QueueReason.QueueDueBusy: 0,
                    QueueReason.QueueDueSession: 0,
                    QueueReason.NotDispatch: 0,
                },
            },
            queue={
                QueueReason.QueueDueBusy: 0,
                QueueReason.QueueDueSession: 0,
                QueueReason.NotDispatch: 0,
            }
        )
        d = AverageDecorator()
        result = d(factors)
        self.assertIsNone(result.queue)

    def test_average(self):
        factors = Factors(
            queue_histories={
                30: {
                    QueueReason.QueueDueBusy: 9,
                    QueueReason.QueueDueSession: 9,
                    QueueReason.NotDispatch: 9,
                },
                10: {
                    QueueReason.QueueDueBusy: 1,
                    QueueReason.QueueDueSession: 2,
                    QueueReason.NotDispatch: 3,
                },
                20: {
                    QueueReason.QueueDueBusy: 2,
                    QueueReason.QueueDueSession: 4,
                    QueueReason.NotDispatch: 6,
                },
            },
            queue={
                QueueReason.QueueDueBusy: 3,
                QueueReason.QueueDueSession: 6,
                QueueReason.NotDispatch: 9,
            }
        )
        d = AverageDecorator(2)
        result = d(factors)
        self.assertIsNotNone(result.queue)
        self.assertEqual(2, result.queue[QueueReason.QueueDueBusy])
        self.assertEqual(4, result.queue[QueueReason.QueueDueSession])
        self.assertEqual(6, result.queue[QueueReason.NotDispatch])

    def test_average_workers(self):
        factors = Factors(
            queue_histories={
                30: {
                    QueueReason.QueueDueBusy: 9,
                    QueueReason.QueueDueSession: 9,
                    QueueReason.NotDispatch: 9,
                },
                10: {
                    QueueReason.QueueDueBusy: 1,
                    QueueReason.QueueDueSession: 2,
                    QueueReason.NotDispatch: 3,
                },
                20: {
                    QueueReason.QueueDueBusy: 2,
                    QueueReason.QueueDueSession: 4,
                    QueueReason.NotDispatch: 6,
                },
            },
            queue={
                QueueReason.QueueDueBusy: 3,
                QueueReason.QueueDueSession: 6,
                QueueReason.NotDispatch: 9,
            },
            worker={
                WorkerStatus.Inflight: 3,
                WorkerStatus.Free: 6,
                WorkerStatus.Busy: 9,
            },
            worker_histories={
                30: {
                    WorkerStatus.Inflight: 9,
                    WorkerStatus.Free: 0,
                    WorkerStatus.Busy: 9,
                },
                10: {
                    WorkerStatus.Inflight: 1,
                    WorkerStatus.Free: 2,
                    WorkerStatus.Busy: 3,
                },
                20: {
                    WorkerStatus.Inflight: 2,
                    WorkerStatus.Free: 4,
                    WorkerStatus.Busy: 6,
                },
            }
        )
        d = AverageDecorator(2)
        result = d(factors)
        self.assertIsNotNone(result.queue)
        self.assertEqual(2, result.queue[QueueReason.QueueDueBusy])
        self.assertEqual(4, result.queue[QueueReason.QueueDueSession])
        self.assertEqual(6, result.queue[QueueReason.NotDispatch])

        self.assertIsNotNone(result.worker)
        self.assertEqual(2, result.worker[WorkerStatus.Inflight])
        self.assertEqual(4, result.worker[WorkerStatus.Free])
        self.assertEqual(6, result.worker[WorkerStatus.Busy])

    def test_ensure_inflight(self):
        factors = Factors(
            worker={
                WorkerStatus.Inflight: 1,
                WorkerStatus.Free: 6,
                WorkerStatus.Busy: 9,
            },
            worker_histories={
                30: {
                    WorkerStatus.Inflight: 0,
                    WorkerStatus.Free: 0,
                    WorkerStatus.Busy: 9,
                },
                10: {
                    WorkerStatus.Inflight: 0,
                    WorkerStatus.Free: 2,
                    WorkerStatus.Busy: 3,
                },
                20: {
                    WorkerStatus.Inflight: 0,
                    WorkerStatus.Free: 4,
                    WorkerStatus.Busy: 6,
                },
            }
        )
        d = AverageDecorator(3)
        result = d(factors)
        self.assertIsNotNone(result.worker)
        self.assertEqual(1, result.worker[WorkerStatus.Inflight])