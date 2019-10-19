import asyncio
import dataclasses
import datetime
import uuid
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from functools import partial
from typing import Any, Callable, Dict, TypedDict

from jsondaora import jsondaora

from ..asgi.router import Controller
from ..exceptions import BadRequestError, InvalidTasksDatabaseError
from ..method import MethodType
from ..route.factory import make_route


try:
    import aioredis
except Exception:
    aioredis = None


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
    controller: Callable[..., Any],
    path_pattern: str,
    max_workers: int = 10,
    tasks_database: Any = None,
) -> BackgroundTask:
    if tasks_database is None:
        tasks_database = SimpleTasksDatabase({})

    elif isinstance(tasks_database, str) and tasks_database.startswith(
        'redis://'
    ):
        if aioredis is None:
            raise InvalidTasksDatabaseError("'aioredis' package not found!")

        tasks_database = partial(get_redis_tasks_database, tasks_database)

    elif aioredis is not None and isinstance(tasks_database, aioredis.Redis):
        tasks_database = RedisTasksDatabase(tasks_database)

    else:
        raise InvalidTasksDatabaseError(tasks_database)

    executor = ThreadPoolExecutor(max_workers)
    annotations = getattr(controller, '__annotations__', {})

    async def create_task(*args: Any, **kwargs: Any) -> TaskInfo:
        task_id = uuid.uuid4()

        if asyncio.iscoroutinefunction(controller):
            loop = asyncio.get_running_loop()

            if callable(tasks_database):

                async def wrapper() -> Any:
                    tasks_database = await tasks_database()  # noqa
                    result = await controller(*args, **kwargs)
                    task = await tasks_database.get(task_id)
                    finished_task = TaskFinishedInfo(
                        end_time=get_iso_time(), result=result, **task  # type: ignore
                    )
                    await tasks_database.set(task_id, finished_task)

            else:

                async def wrapper() -> Any:
                    result = await controller(*args, **kwargs)
                    task = await tasks_database.get(task_id)
                    finished_task = TaskFinishedInfo(
                        end_time=get_iso_time(), result=result, **task  # type: ignore
                    )
                    await tasks_database.set(task_id, finished_task)

            future = asyncio.run_coroutine_threadsafe(wrapper(), loop)

        else:

            def done_callback(future: Any) -> None:
                result = future.result()
                policy = asyncio.get_event_loop_policy()
                loop = policy.new_event_loop()
                task = loop.run_until_complete(tasks_database.get(task_id))
                finished_task = TaskFinishedInfo(
                    end_time=get_iso_time(), result=result, **task  # type: ignore
                )
                loop.run_until_complete(
                    tasks_database.set(task_id, finished_task)
                )

            future = executor.submit(controller, *args, **kwargs)
            future.add_done_callback(done_callback)

        start_time = get_iso_time()
        task = TaskInfo(
            task_id=str(task_id),
            start_time=start_time,
            status=TaskStatusType.RUNNING.value,
        )
        await tasks_database.set(task_id, task)
        return task

    async def get_task_results(task_id: str) -> TaskInfo:
        try:
            return await tasks_database.get(uuid.UUID(task_id))  # type: ignore
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


@dataclasses.dataclass
class SimpleTasksDatabase:
    data_source: Dict[str, Any]

    async def set(self, key: Any, value: Any) -> None:
        self.data_source[key] = value

    async def get(self, key: Any) -> Any:
        return self.data_source[key]


if aioredis is not None:

    @dataclasses.dataclass
    class RedisTasksDatabase:
        data_source: aioredis.Redis

        async def set(self, key: Any, value: Any) -> None:
            ...

        async def get(self, key: Any) -> Any:
            ...

    async def get_redis_tasks_database(uri: str) -> RedisTasksDatabase:
        data_source = await aioredis.create_redis_pool(uri)
        return RedisTasksDatabase(data_source)
