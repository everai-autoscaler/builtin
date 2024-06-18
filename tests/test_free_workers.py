import datetime
import unittest

from everai_autoscaler.model import AutoScaler, BuiltinAutoScaler, Factors, ScaleUpAction, QueueReason, ScaleDownAction
from everai_autoscaler.model.factors import  WorkerStatus

from everai_autoscaler.builtin import FreeWorkerAutoScaler
from .test_utils import make_worker


def f(a: AutoScaler):
    ...


def f2(b: BuiltinAutoScaler):
    ...


class TestSimple(unittest.TestCase):
    def test_simple(self):
        s: BuiltinAutoScaler = FreeWorkerAutoScaler()
        f(s)

        s.decide(Factors(
            queue=dict(),
            workers=[]
        ))

    def test_initial_scaleup(self):
        s: BuiltinAutoScaler = FreeWorkerAutoScaler(
            scale_up_step=2,
            max_workers=3,
        )
        result = s.decide(Factors(
            queue=dict(),
            workers=[]
        ))
        self.assertEqual(1, len(result.actions))
        self.assertIsInstance(result.actions[0], ScaleUpAction)
        self.assertEqual(1, result.actions[0].count)

    def test_scaleup(self):
        s: BuiltinAutoScaler = FreeWorkerAutoScaler(
            scale_up_step=2,
            min_free_workers=1,
            max_workers=3,
        )
        result = s.decide(Factors(
            queue={
                QueueReason.QueueDueBusy: 0,
                QueueReason.NotDispatch: 0,
                QueueReason.QueueDueSession: 0,
            },
            workers=[
                make_worker(status=WorkerStatus.Busy),
            ]
        ))
        self.assertEqual(1, len(result.actions))
        self.assertIsInstance(result.actions[0], ScaleUpAction)
        self.assertEqual(2, result.actions[0].count)

    def test_scaleup_max_workers_limit(self):
        s: BuiltinAutoScaler = FreeWorkerAutoScaler(
            scale_up_step=2,
            max_workers=3,
        )
        result = s.decide(Factors(
            queue={
                QueueReason.QueueDueBusy: 0,
                QueueReason.NotDispatch: 0,
                QueueReason.QueueDueSession: 0,
            },
            workers=[
                make_worker(status=WorkerStatus.Busy),
                make_worker(status=WorkerStatus.Busy),
            ]
        ))
        self.assertEqual(1, len(result.actions))
        self.assertIsInstance(result.actions[0], ScaleUpAction)
        self.assertEqual(1, result.actions[0].count)

    def test_scaleup_max_workers_arrived(self):
        s: BuiltinAutoScaler = FreeWorkerAutoScaler(
            scale_up_step=2,
            max_workers=3,
        )
        result = s.decide(Factors(
            queue={
                QueueReason.QueueDueBusy: 3,
                QueueReason.NotDispatch: 0,
                QueueReason.QueueDueSession: 0,
            },
            workers=[
                make_worker(status=WorkerStatus.Busy),
                make_worker(status=WorkerStatus.Busy),
                make_worker(status=WorkerStatus.Busy),
            ]
        ))
        self.assertEqual(0, len(result.actions))

    def test_scaledown(self):
        s: BuiltinAutoScaler = FreeWorkerAutoScaler(
            scale_up_step=2,
            max_workers=3,
        )
        now_timestamp = int(datetime.datetime.now().timestamp())
        before_180 = now_timestamp - 180

        free_worker = make_worker(status=WorkerStatus.Free, last_service_time=before_180)
        result = s.decide(Factors(
            queue={
                QueueReason.QueueDueBusy: 0,
                QueueReason.NotDispatch: 0,
                QueueReason.QueueDueSession: 0,
            },
            workers=[
                make_worker(status=WorkerStatus.Free),
                make_worker(status=WorkerStatus.Free),
                free_worker
            ]
        ))
        self.assertEqual(1, len(result.actions))
        self.assertIsInstance(result.actions[0], ScaleDownAction)
        self.assertEqual(free_worker.worker_id, result.actions[0].worker_id)
