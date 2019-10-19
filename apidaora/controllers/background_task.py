import asyncio
import dataclasses
import datetime
import uuid
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from typing import Any, Callable, Dict, TypedDict, Union

from jsondaora import jsondaora

from ..asgi.router import Controller
from ..exceptions import BadRequestError
from ..method import MethodType
from ..route.factory import make_route


class TaskStatusType(Enum):
    RUNNING = 'running'
    FINISHED = 'finished'
    ERROR = 'error'


@jsondaora
class TaskInfo(TypedDict):
    task_id: str
    start_time: str
    status: str


@jsondaora
class TaskFinishedInfo(TaskInfo):
    end_time: str
    result: Any


@dataclasses.dataclass
class BackgroundTask:
    create: Controller
    get_results: Controller


def make_background_task(
    controller: Callable[..., Any], path_pattern: str, max_workers: int = 10
) -> BackgroundTask:
    TASKS_DB: Dict[uuid.UUID, Union[TaskInfo, TaskFinishedInfo]] = {}
    executor = ThreadPoolExecutor(max_workers)
    annotations = getattr(controller, '__annotations__', {})

    def create_task(*args: Any, **kwargs: Any) -> TaskInfo:
        task_id = uuid.uuid4()

        def done_callback(future: Any) -> None:
            result = future.result()
            task = TASKS_DB[task_id]
            finished_task = TaskFinishedInfo(
                end_time=get_iso_time(), result=result, **task  # type: ignore
            )
            TASKS_DB[task_id] = finished_task

        if asyncio.iscoroutinefunction(controller):
            loop = asyncio.get_running_loop()
            future = asyncio.run_coroutine_threadsafe(
                controller(*args, **kwargs), loop
            )
            future.add_done_callback(done_callback)

        else:
            future = executor.submit(controller, *args, **kwargs)
            future.add_done_callback(done_callback)

        start_time = get_iso_time()
        task = TaskInfo(
            task_id=str(task_id),
            start_time=start_time,
            status=TaskStatusType.RUNNING.value,
        )
        TASKS_DB[task_id] = task
        return task

    def get_task_results(task_id: str) -> TaskInfo:
        try:
            return TASKS_DB[uuid.UUID(task_id)]
        except KeyError:
            raise BadRequestError(
                name='invalid_task_id', info={'task_id': task_id}
            )
        except ValueError as error:
            if error.args == ('badly formed hexadecimal UUID string',):
                raise BadRequestError(
                    name='invalid_task_id', info={'task_id': task_id}
                )

            raise error from None

    create_task.__annotations__ = {
        name: type_ for name, type_ in annotations.items() if name != 'return'
    }

    return BackgroundTask(
        make_route(path_pattern, MethodType.POST, create_task).controller,
        make_route(path_pattern, MethodType.GET, get_task_results).controller,
    )


def get_iso_time() -> str:
    return (
        datetime.datetime.now()
        .replace(microsecond=0, tzinfo=datetime.timezone.utc)
        .isoformat()
    )
