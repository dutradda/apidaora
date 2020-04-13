import asyncio
import dataclasses
import datetime
import hashlib
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from functools import partial
from http import HTTPStatus
from typing import Any, Callable, Coroutine, Dict, Optional, Type, TypedDict

import orjson
from jsondaora import as_typed_dict, jsondaora, typed_dict_asjson

from ..asgi.router import Controller
from ..exceptions import BadRequestError, InvalidTasksRepositoryError
from ..method import MethodType
from ..middlewares import Middlewares
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
    signature: str


@dataclasses.dataclass
class BackgroundTask:
    create: Controller
    get_results: Controller


def make_background_task(
    controller: Callable[..., Any],
    path_pattern: str,
    max_workers: int = 10,
    tasks_repository_uri: Optional[str] = None,
    lock: bool = False,
    lock_args: bool = False,
    middlewares: Optional[Middlewares] = None,
    options: bool = False,
) -> BackgroundTask:
    if asyncio.iscoroutinefunction(controller):
        logger.warning(
            'Async tasks can potentially block your application, use with care. '
            'It use is recommended just for small tasks or non-blocking operations.'
        )

    annotations = getattr(controller, '__annotations__', {})
    result_annotation = annotations.get('return', str)
    signature = hashlib.md5(
        '-'.join(
            [controller.__name__]
            + [
                '-'.join((name, type_.__name__))
                for name, type_ in annotations.items()
            ]
        ).encode()
    ).hexdigest()[:12]
    server_id = uuid.uuid4()
    tasks_repository_builder = get_tasks_repository_builder(
        tasks_repository_uri, server_id, signature
    )

    @jsondaora
    class FinishedTaskInfo(TaskInfo):
        end_time: str
        result: result_annotation  # type: ignore

    create_task = make_create_task(
        controller,
        tasks_repository_builder,
        FinishedTaskInfo,
        max_workers,
        lock,
        lock_args,
        signature,
    )
    get_task_results = make_get_task_results(
        tasks_repository_builder, FinishedTaskInfo, lock, lock_args
    )

    create_task.__annotations__ = {
        name: type_ for name, type_ in annotations.items() if name != 'return'
    }

    return BackgroundTask(
        make_route(
            path_pattern,
            MethodType.POST,
            create_task,
            route_middlewares=middlewares,
            options=options,
        ).controller,
        make_route(
            path_pattern,
            MethodType.GET,
            get_task_results,
            route_middlewares=middlewares,
            options=options,
        ).controller,
    )


def get_iso_time() -> str:
    return (
        datetime.datetime.now()
        .replace(microsecond=0, tzinfo=datetime.timezone.utc)
        .isoformat()
    )


@dataclasses.dataclass
class BaseTasksRepository:
    server_id: uuid.UUID
    signature: str
    data_source: Any

    async def set(
        self,
        value: Any,
        task_cls: Type[Any] = TaskInfo,
        task_id: Optional[str] = None,
    ) -> None:
        raise NotImplementedError()

    async def get(
        self, finished_task_cls: Type[Any], task_id: Optional[str] = None,
    ) -> Any:
        raise NotImplementedError()

    async def close(self) -> None:
        ...

    def build_key(self, task_id: Optional[str]) -> str:
        base_key = f'apidaora:{self.server_id}:{self.signature}'

        if task_id:
            return f'{base_key}:{task_id}'

        return base_key


@dataclasses.dataclass
class SimpleTasksRepository(BaseTasksRepository):
    data_source: Dict[str, Any]

    async def set(
        self,
        value: Any,
        task_cls: Type[Any] = TaskInfo,
        task_id: Optional[str] = None,
    ) -> None:
        self.data_source[self.build_key(task_id)] = value

    async def get(
        self, finished_task_cls: Type[Any], task_id: Optional[str] = None,
    ) -> Any:
        return self.data_source[self.build_key(task_id)]


def get_tasks_repository_builder(
    uri: Optional[str], server_id: uuid.UUID, signature: str
) -> Any:
    if uri is None:

        async def builder() -> SimpleTasksRepository:
            return SimpleTasksRepository(server_id, signature, TASKS_DB)

        return builder

    elif isinstance(uri, str) and uri.startswith('redis://'):
        if aioredis is None:
            raise InvalidTasksRepositoryError("'aioredis' package not found!")

        return partial(
            get_redis_tasks_repository,
            server_id=server_id,
            signature=signature,
            uri=uri,
        )

    raise InvalidTasksRepositoryError(uri)


def make_create_task(
    controller: Callable[..., Any],
    tasks_repository_builder: Any,
    finished_task_info_cls: Any,
    max_workers: int,
    lock: bool,
    lock_args: bool,
    signature: str,
) -> Callable[..., Coroutine[Any, Any, Response]]:
    executor = ThreadPoolExecutor(max_workers)

    async def create_task(*args: Any, **kwargs: Any) -> Response:
        if lock_args:
            task_id = hashlib.md5(
                '-'.join(
                    [str(arg) for arg in args]
                    + [
                        '-'.join((key, str(value)))
                        for key, value in kwargs.items()
                    ]
                ).encode()
            ).hexdigest()[:12]
        else:
            task_id = str(uuid.uuid4())

        task_key = None if lock else task_id
        tasks_repository = await tasks_repository_builder()
        lock_error = await get_lock_error(
            lock, lock_args, tasks_repository, finished_task_info_cls, task_key
        )

        if lock_error:
            raise lock_error

        if asyncio.iscoroutinefunction(controller):
            wrapper = make_controller_wrapper(
                tasks_repository_builder,
                finished_task_info_cls,
                task_key,
                controller,
                *args,
                **kwargs,
            )
            task_ = asyncio.create_task(wrapper())
            task_.add_done_callback(lambda f: f.result())

        else:
            done_callback = make_done_callback(
                tasks_repository_builder, task_key, finished_task_info_cls
            )
            future = executor.submit(controller, *args, **kwargs)
            future.add_done_callback(done_callback)

        start_time = get_iso_time()

        task = TaskInfo(
            task_id=str(task_id),
            start_time=start_time,
            status=TaskStatusType.RUNNING.value,
            signature=signature,
        )
        await tasks_repository.set(
            task, task_cls=finished_task_info_cls, task_id=task_key
        )
        await tasks_repository.close()

        return json(task, status=HTTPStatus.CREATED)

    return create_task


def make_controller_wrapper(
    tasks_repository_builder: Any,
    finished_task_info_cls: Any,
    task_key: Optional[str],
    controller: Any,
    *args: Any,
    **kwargs: Any,
) -> Callable[..., Coroutine[Any, Any, TaskInfo]]:
    async def wrapper() -> Any:
        tasks_repository = await tasks_repository_builder()

        try:
            result = await controller(*args, **kwargs)
            status = TaskStatusType.FINISHED.value
        except Exception:
            logger.exception(
                f'server-id={tasks_repository.server_id}; '
                f'signature={tasks_repository.signature}; '
                f'task-key={task_key};'
            )
            result = None
            status = TaskStatusType.ERROR.value

        task = await tasks_repository.get(
            finished_task_info_cls, task_id=task_key
        )
        finished_task = finished_task_info_cls(
            end_time=get_iso_time(),
            result=result,
            status=status,
            task_id=task['task_id'],
            start_time=task['start_time'],
            signature=task['signature'],
        )
        await tasks_repository.set(
            finished_task, task_cls=finished_task_info_cls, task_id=task_key
        )
        await tasks_repository.close()

    return wrapper


def make_done_callback(
    tasks_repository_builder: Any,
    task_key: Optional[str],
    finished_task_info_cls: Any,
) -> Callable[[Any], None]:
    def done_callback(future: Any) -> None:
        policy = asyncio.get_event_loop_policy()
        loop = policy.new_event_loop()
        tasks_repository = loop.run_until_complete(tasks_repository_builder())

        try:
            result = future.result()
            status = TaskStatusType.FINISHED.value
        except Exception:
            logger.exception(
                f'server-id={tasks_repository.server_id}; '
                f'signature={tasks_repository.signature}; '
                f'task-key={task_key};'
            )
            result = None
            status = TaskStatusType.ERROR.value

        task = loop.run_until_complete(
            tasks_repository.get(finished_task_info_cls, task_id=task_key)
        )

        finished_task = finished_task_info_cls(
            end_time=get_iso_time(),
            result=result,
            status=status,
            task_id=task['task_id'],
            start_time=task['start_time'],
            signature=task['signature'],
        )

        loop.run_until_complete(
            tasks_repository.set(
                finished_task,
                task_cls=finished_task_info_cls,
                task_id=task_key,
            )
        )
        loop.run_until_complete(tasks_repository.close())

    return done_callback


def make_get_task_results(
    tasks_repository_builder: Any,
    finished_task_info_cls: Any,
    lock: bool,
    lock_args: bool,
) -> Callable[..., Coroutine[Any, Any, TaskInfo]]:
    async def get_task_results(task_id: str) -> finished_task_info_cls:  # type: ignore
        task_key = None if lock else (task_id if lock_args else task_id)
        tasks_repository = await tasks_repository_builder()

        try:
            task = await tasks_repository.get(
                finished_task_info_cls, task_id=task_key
            )
            return task  # type: ignore
        except KeyError:
            raise BadRequestError(
                name='invalid-task-id', info={'task_id': task_id}
            )
        except ValueError as error:
            if error.args == ('badly formed hexadecimal UUID string',):
                raise BadRequestError(
                    name='invalid-task-id', info={'task_id': task_id}
                )

            raise error from None
        finally:
            await tasks_repository.close()

    return get_task_results


async def get_lock_error(
    lock: bool,
    lock_args: bool,
    tasks_repository: BaseTasksRepository,
    finished_task_info_cls: Any,
    task_key: Optional[str],
) -> Optional[BadRequestError]:
    if lock or lock_args:
        try:
            task = await tasks_repository.get(
                finished_task_info_cls, task_id=task_key
            )
            if task['status'] == TaskStatusType.RUNNING.value:
                if lock_args:
                    return BadRequestError(
                        'lock-args', {'task_id': task['task_id']}
                    )

                return BadRequestError(
                    'lock', {'signature': task['signature']}
                )

        except KeyError:
            ...

    return None


if aioredis is not None:

    @dataclasses.dataclass
    class RedisTasksRepository(BaseTasksRepository):
        data_source: aioredis.Redis

        async def set(
            self,
            value: Any,
            task_cls: Type[Any] = TaskInfo,
            task_id: Optional[str] = None,
        ) -> None:
            await self.data_source.set(
                self.build_key(task_id), typed_dict_asjson(value, task_cls)
            )

        async def get(
            self, finished_task_cls: Type[Any], task_id: Optional[str] = None,
        ) -> Any:
            value = await self.data_source.get(self.build_key(task_id))

            if value:
                value = orjson.loads(value)

                if value['status'] == TaskStatusType.RUNNING.value:
                    return as_typed_dict(value, TaskInfo)

                if value['status'] == TaskStatusType.FINISHED.value:
                    return as_typed_dict(value, finished_task_cls)

            raise KeyError(self.build_key(task_id))

        async def close(self) -> None:
            self.data_source.close()
            await self.data_source.wait_closed()

    async def get_redis_tasks_repository(
        server_id: uuid.UUID, signature: str, uri: str
    ) -> RedisTasksRepository:
        data_source = await aioredis.create_redis_pool(uri)
        return RedisTasksRepository(server_id, signature, data_source)


TASKS_DB: Dict[str, Any] = {}
