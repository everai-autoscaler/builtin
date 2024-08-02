import datetime
import typing
import uuid

from everai_autoscaler.model import WorkerStatus
from everai_autoscaler.model.factors import Worker


def make_worker(
        worker_id: typing.Optional[str] = None,
        gpu_type: typing.Optional[str] = None,
        region: str = 'us-east-1',
        started_at: typing.Optional[int] = None,
        last_service_time: typing.Optional[int] = None,
        number_of_successes: int = 0,
        number_of_failures: int = 0,
        number_of_sessions: int = 0,
        average_response_time: float = 0.3,
        current_request: int = 0,
        status: WorkerStatus = WorkerStatus.Free) -> Worker:
    worker_id = worker_id or str(uuid.uuid4())
    now_timestamp = int(datetime.datetime.now().timestamp())
    started_at = started_at or now_timestamp
    last_service_time = last_service_time or now_timestamp
    return Worker(
        worker_id=worker_id,
        gpu_type=gpu_type,
        region=region,
        started_at=started_at,
        last_service_time=last_service_time,
        number_of_successes=number_of_successes,
        number_of_failures=number_of_failures,
        number_of_sessions=number_of_sessions,
        average_response_time=average_response_time,
        current_request=current_request,
        status=status
    )
