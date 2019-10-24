import asyncio
import dataclasses
import datetime
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from functools import partial
from http import HTTPStatus
from typing import Any, Callable, Coroutine, Dict, Type, TypedDict

import orjson
from jsondaora import as_typed_dict, jsondaora, typed_dict_asjson

from ..asgi.router import Controller
from ..exceptions import BadRequestError, InvalidTasksRepositoryError
from ..method import MethodType
from ..responses import Response, json
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
    tasks_repository: Any = None,
) -> BackgroundTask:
    if asyncio.iscoroutinefunction(controller):
        logger.warning(
            'Async tasks can potentially block your application, use with care. '
            'It use is recommended just for small tasks or non-blocking operations.'
        )

    tasks_repository = get_tasks_repository(tasks_repository)

    annotations = getattr(controller, '__annotations__', {})
    result_annotation = annotations.get('return', str)

    @jsondaora
    class FinishedTaskInfo(TaskInfo):
        end_time: str
        result: result_annotation  # type: ignore

    create_task = make_create_task(
        controller, tasks_repository, FinishedTaskInfo, max_workers
    )
    get_task_results = make_get_task_results(
        tasks_repository, FinishedTaskInfo
    )

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
class BaseTasksRepository:
    async def set(
        self, key: Any, value: Any, task_cls: Type[Any] = TaskInfo
    ) -> None:
        ...

    async def get(self, key: Any, finished_task_cls: Type[Any]) -> Any:
        ...

    def close(self) -> None:
        ...


@dataclasses.dataclass
class SimpleTasksRepository(BaseTasksRepository):
    data_source: Dict[str, Any]

    async def set(
        self, key: Any, value: Any, task_cls: Type[Any] = TaskInfo
    ) -> None:
        self.data_source[key] = value

    async def get(self, key: Any, finished_task_cls: Type[Any]) -> Any:
        return self.data_source[key]


def get_tasks_repository(tasks_repository: Any) -> Any:
    if tasks_repository is None:
        return SimpleTasksRepository({})

    elif isinstance(tasks_repository, str) and tasks_repository.startswith(
        'redis://'
    ):
        if aioredis is None:
            raise InvalidTasksRepositoryError("'aioredis' package not found!")

        return partial(get_redis_tasks_repository, tasks_repository)

    elif isinstance(tasks_repository, BaseTasksRepository):
        return tasks_repository

    raise InvalidTasksRepositoryError(tasks_repository)


def make_create_task(
    controller: Callable[..., Any],
    tasks_repository_: Any,
    finished_task_info_cls: Any,
    max_workers: int,
) -> Callable[..., Coroutine[Any, Any, Response]]:
    executor = ThreadPoolExecutor(max_workers)

    async def create_task(*args: Any, **kwargs: Any) -> Response:
        task_id = uuid.uuid4()
        tasks_repository = tasks_repository_

        if asyncio.iscoroutinefunction(controller):
            if isinstance(tasks_repository, partial):
                tasks_repository = await tasks_repository()

            loop = asyncio.get_running_loop()
            wrapper = make_task_wrapper(
                tasks_repository,
                task_id,
                finished_task_info_cls,
                controller,
                *args,
                **kwargs,
            )
            asyncio.run_coroutine_threadsafe(wrapper(), loop)

        else:
            done_callback = make_done_callback(
                tasks_repository, task_id, finished_task_info_cls
            )

            future = executor.submit(controller, *args, **kwargs)
            future.add_done_callback(done_callback)

        start_time = get_iso_time()
        task = TaskInfo(
            task_id=str(task_id),
            start_time=start_time,
            status=TaskStatusType.RUNNING.value,
        )

        if isinstance(tasks_repository, partial):
            tasks_repository = await tasks_repository()

        await tasks_repository.set(
            task_id, task, task_cls=finished_task_info_cls
        )

        if not asyncio.iscoroutinefunction(controller):
            tasks_repository.close()

        return json(task, status=HTTPStatus.CREATED)

    return create_task


def make_task_wrapper(
    tasks_repository: Any,
    task_id: uuid.UUID,
    finished_task_info_cls: Any,
    controller: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> Callable[..., Coroutine[Any, Any, TaskInfo]]:
    async def wrapper() -> Any:
        result = await controller(*args, **kwargs)
        task = await tasks_repository.get(task_id, finished_task_info_cls)
        finished_task = finished_task_info_cls(
            end_time=get_iso_time(),
            result=result,
            status=TaskStatusType.FINISHED.value,
            task_id=task['task_id'],
            start_time=task['start_time'],
        )
        await tasks_repository.set(
            task_id, finished_task, task_cls=finished_task_info_cls
        )
        tasks_repository.close()

    return wrapper


def make_done_callback(
    tasks_repository_: Any, task_id: uuid.UUID, finished_task_info_cls: Any
) -> Callable[[Any], None]:
    def done_callback(future: Any) -> None:
        result = future.result()
        policy = asyncio.get_event_loop_policy()
        loop = policy.new_event_loop()
        tasks_repository = tasks_repository_

        if isinstance(tasks_repository, partial):
            tasks_repository = loop.run_until_complete(tasks_repository())

        task = loop.run_until_complete(
            tasks_repository.get(task_id, finished_task_info_cls)
        )
        finished_task = finished_task_info_cls(
            end_time=get_iso_time(),
            result=result,
            status=TaskStatusType.FINISHED.value,
            task_id=task['task_id'],
            start_time=task['start_time'],
        )
        loop.run_until_complete(
            tasks_repository.set(
                task_id, finished_task, task_cls=finished_task_info_cls
            )
        )
        tasks_repository.close()

    return done_callback


def make_get_task_results(
    tasks_repository_: Any, finished_task_info_cls: Any
) -> Callable[..., Coroutine[Any, Any, TaskInfo]]:
    async def get_task_results(task_id: str) -> finished_task_info_cls:  # type: ignore
        tasks_repository = tasks_repository_

        if isinstance(tasks_repository, partial):
            tasks_repository = await tasks_repository()

        try:
            task = await tasks_repository.get(
                uuid.UUID(task_id), finished_task_info_cls
            )
            tasks_repository.close()
            return task  # type: ignore
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

    return get_task_results


if aioredis is not None:

    @dataclasses.dataclass
    class RedisTasksRepository(BaseTasksRepository):
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

        def close(self) -> None:
            self.data_source.close()

    async def get_redis_tasks_repository(uri: str) -> RedisTasksRepository:
        data_source = await aioredis.create_redis_pool(uri)
        return RedisTasksRepository(data_source)
