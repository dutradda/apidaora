import asyncio
import dataclasses
import datetime
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from functools import partial
from typing import Any, Callable, Dict, Type, TypedDict

import orjson
from jsondaora import as_typed_dict, jsondaora, typed_dict_asjson

from ..asgi.router import Controller
from ..exceptions import BadRequestError, InvalidTasksDatabaseError
from ..method import MethodType
from ..route.factory import make_route


logger = logging.getLogger(__name__)


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
    if asyncio.iscoroutinefunction(controller):
        logger.warning(
            'Async tasks can potentially block yours application, use with care. '
            'It use is recommended just for small tasks or non-blocking operations.'
        )

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
    Result = annotations.get('return', str)

    @jsondaora
    class FinishedTaskInfo(TaskInfo):
        end_time: str
        result: Result  # type: ignore

    async def create_task(*args: Any, **kwargs: Any) -> TaskInfo:
        task_id = uuid.uuid4()

        if asyncio.iscoroutinefunction(controller):
            loop = asyncio.get_running_loop()

            if isinstance(tasks_database, partial):
                tasks_database_ = await tasks_database()  # noqa
            else:
                tasks_database_ = tasks_database

            async def wrapper() -> Any:
                result = await controller(*args, **kwargs)
                task = await tasks_database_.get(task_id, FinishedTaskInfo)
                finished_task = FinishedTaskInfo(
                    end_time=get_iso_time(),
                    result=result,
                    status=TaskStatusType.FINISHED.value,
                    task_id=task['task_id'],
                    start_time=task['start_time'],
                )
                await tasks_database_.set(
                    task_id, finished_task, task_cls=FinishedTaskInfo
                )

            future = asyncio.run_coroutine_threadsafe(wrapper(), loop)

        else:

            def done_callback(future: Any) -> None:
                result = future.result()
                policy = asyncio.get_event_loop_policy()
                loop = policy.new_event_loop()
                if isinstance(tasks_database, partial):
                    tasks_database_ = loop.run_until_complete(tasks_database())
                else:
                    tasks_database_ = tasks_database

                task = loop.run_until_complete(
                    tasks_database_.get(task_id, FinishedTaskInfo)
                )
                finished_task = FinishedTaskInfo(
                    end_time=get_iso_time(),
                    result=result,
                    status=TaskStatusType.FINISHED.value,
                    task_id=task['task_id'],
                    start_time=task['start_time'],
                )
                loop.run_until_complete(
                    tasks_database_.set(
                        task_id, finished_task, task_cls=FinishedTaskInfo
                    )
                )

            future = executor.submit(controller, *args, **kwargs)
            future.add_done_callback(done_callback)

        start_time = get_iso_time()
        task = TaskInfo(
            task_id=str(task_id),
            start_time=start_time,
            status=TaskStatusType.RUNNING.value,
        )

        if isinstance(tasks_database, partial):
            tasks_database_ = await tasks_database()  # noqa
        else:
            tasks_database_ = tasks_database

        await tasks_database_.set(task_id, task, task_cls=FinishedTaskInfo)
        return task

    async def get_task_results(task_id: str) -> FinishedTaskInfo:
        if isinstance(tasks_database, partial):
            tasks_database_ = await tasks_database()  # noqa
        else:
            tasks_database_ = tasks_database

        try:
            return await tasks_database_.get(  # type: ignore
                uuid.UUID(task_id), FinishedTaskInfo
            )
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

    async def set(
        self, key: Any, value: Any, task_cls: Type[Any] = TaskInfo
    ) -> None:
        self.data_source[key] = value

    async def get(self, key: Any, finished_task_cls: Type[Any]) -> Any:
        return self.data_source[key]


if aioredis is not None:

    @dataclasses.dataclass
    class RedisTasksDatabase:
        data_source: aioredis.Redis

        async def set(
            self, key: Any, value: Any, task_cls: Type[Any] = TaskInfo
        ) -> None:
            await self.data_source.set(
                str(key), typed_dict_asjson(value, task_cls)
            )

        async def get(self, key: Any, finished_task_cls: Type[Any]) -> Any:
            value = await self.data_source.get(str(key))

            if value:
                value = orjson.loads(value)

                if value['status'] == TaskStatusType.RUNNING.value:
                    return as_typed_dict(value, TaskInfo)

                if value['status'] == TaskStatusType.FINISHED.value:
                    return as_typed_dict(value, finished_task_cls)

            raise KeyError(key)

    async def get_redis_tasks_database(uri: str) -> RedisTasksDatabase:
        data_source = await aioredis.create_redis_pool(uri)
        return RedisTasksDatabase(data_source)
