import unittest

from everai_autoscaler.model import Factors, QueueReason

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
        self.assertIsNone(result)

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
        self.assertIsNone(result)

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
        self.assertIsNotNone(result)
        self.assertEqual(2, result.queue[QueueReason.QueueDueBusy])
        self.assertEqual(4, result.queue[QueueReason.QueueDueSession])
        self.assertEqual(6, result.queue[QueueReason.NotDispatch])

