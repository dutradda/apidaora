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
from typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Dict,
    Optional,
    Type,
    TypedDict,
)

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
    args_signature: Optional[str]


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
        tasks_repository_builder, FinishedTaskInfo
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
    tasks_repository_builder: Callable[[], Awaitable['BaseTasksRepository']],
    finished_task_info_cls: Any,
    max_workers: int,
    lock: bool,
    lock_args: bool,
    signature: str,
) -> Callable[..., Coroutine[Any, Any, Response]]:
    executor = ThreadPoolExecutor(max_workers)

    async def create_task(*args: Any, **kwargs: Any) -> Response:
        task_id = str(uuid.uuid4())
        args_signature = None

        if lock_args:
            args_signature = hashlib.md5(
                '-'.join(
                    [str(arg) for arg in args]
                    + [
                        '-'.join((key, str(value)))
                        for key, value in kwargs.items()
                    ]
                ).encode()
            ).hexdigest()[:12]

        tasks_repository = await tasks_repository_builder()
        lock_error = await get_lock_error(
            tasks_repository, lock, signature, args_signature
        )

        if lock_error:
            await tasks_repository.close()
            raise lock_error

        if lock:
            await tasks_repository.lock_signature()
        elif args_signature:
            await tasks_repository.lock_args_signature(args_signature)

        if asyncio.iscoroutinefunction(controller):
            wrapper = make_controller_wrapper(
                tasks_repository_builder,
                task_id,
                lock,
                args_signature,
                finished_task_info_cls,
                controller,
                *args,
                **kwargs,
            )
            task_ = asyncio.create_task(wrapper())
            task_.add_done_callback(lambda f: f.result())

        else:
            done_callback = make_done_callback(
                tasks_repository_builder,
                task_id,
                lock,
                args_signature,
                finished_task_info_cls,
            )
            future = executor.submit(controller, *args, **kwargs)
            future.add_done_callback(done_callback)

        start_time = get_iso_time()

        task = TaskInfo(
            task_id=str(task_id),
            start_time=start_time,
            status=TaskStatusType.RUNNING.value,
            signature=signature,
            args_signature=args_signature,
        )
        await tasks_repository.set(task, task_id, finished_task_info_cls)
        await tasks_repository.close()

        return json(task, status=HTTPStatus.CREATED)

    return create_task


def make_controller_wrapper(
    tasks_repository_builder: Callable[[], Awaitable['BaseTasksRepository']],
    task_id: str,
    lock: bool,
    args_signature: Optional[str],
    finished_task_info_cls: Any,
    controller: Any,
    *args: Any,
    **kwargs: Any,
) -> Callable[..., Coroutine[Any, Any, TaskInfo]]:
    async def wrapper() -> Any:
        tasks_repository = await tasks_repository_builder()

        try:
            result = await controller(*args, **kwargs)
            status = TaskStatusType.FINISHED.value
        except Exception as error:
            logger.exception(
                f'server-id={tasks_repository.server_id}; '
                f'signature={tasks_repository.signature}; '
                f'args-signature={args_signature};'
                f'task-id={task_id};'
            )
            result = {
                'error': {
                    'name': type(error).__name__,
                    'args': [str(a) for a in error.args],
                }
            }
            status = TaskStatusType.ERROR.value

        task = await tasks_repository.get(task_id, finished_task_info_cls)
        finished_task = finished_task_info_cls(
            end_time=get_iso_time(),
            result=result,
            status=status,
            task_id=task['task_id'],
            start_time=task['start_time'],
            signature=task['signature'],
            args_signature=task['args_signature'],
        )
        await tasks_repository.set(
            finished_task, task_id, finished_task_info_cls
        )

        if lock:
            await tasks_repository.unlock_signature()
        elif args_signature:
            await tasks_repository.unlock_args_signature(args_signature)

        await tasks_repository.close()

    return wrapper


def make_done_callback(
    tasks_repository_builder: Callable[[], Awaitable['BaseTasksRepository']],
    task_id: str,
    lock: bool,
    args_signature: Optional[str],
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
                f'task-key={task_id};'
            )
            result = None
            status = TaskStatusType.ERROR.value

        task = loop.run_until_complete(
            tasks_repository.get(task_id, finished_task_info_cls)
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
                finished_task, task_id, finished_task_info_cls,
            )
        )

        if lock:
            loop.run_until_complete(tasks_repository.unlock_signature())
        elif args_signature:
            loop.run_until_complete(
                tasks_repository.unlock_args_signature(args_signature)
            )

        loop.run_until_complete(tasks_repository.close())

    return done_callback


def make_get_task_results(
    tasks_repository_builder: Callable[[], Awaitable['BaseTasksRepository']],
    finished_task_info_cls: Any,
) -> Callable[..., Coroutine[Any, Any, TaskInfo]]:
    async def get_task_results(task_id: str) -> finished_task_info_cls:  # type: ignore
        tasks_repository = await tasks_repository_builder()

        try:
            task = await tasks_repository.get(task_id, finished_task_info_cls)
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
    tasks_repository: 'BaseTasksRepository',
    lock: bool,
    signature: str,
    args_signature: Optional[str],
) -> Optional[BadRequestError]:
    if lock and await tasks_repository.is_signature_locked():
        return BadRequestError('lock', {'signature': signature})

    if args_signature and await tasks_repository.is_args_locked(
        args_signature
    ):
        return BadRequestError('lock-args', {'args_signature': args_signature})

    return None


@dataclasses.dataclass
class BaseTasksRepository:
    server_id: uuid.UUID
    signature: str
    data_source: Any

    async def set(
        self, value: Any, task_id: str, task_cls: Type[Any] = TaskInfo,
    ) -> None:
        raise NotImplementedError()

    async def get(self, task_id: str, finished_task_cls: Type[Any]) -> Any:
        raise NotImplementedError()

    async def lock_signature(self) -> None:
        raise NotImplementedError()

    async def lock_args_signature(self, args_signature: str) -> None:
        raise NotImplementedError()

    async def is_signature_locked(self) -> bool:
        ...

    async def is_args_locked(self, args_signature: str) -> bool:
        ...

    async def unlock_signature(self) -> Any:
        raise NotImplementedError()

    async def unlock_args_signature(self, args_signature: str) -> Any:
        raise NotImplementedError()

    async def close(self) -> None:
        ...

    def build_signature_key(self) -> str:
        return f'apidaora:{self.server_id}:{self.signature}'

    def build_key(self, task_id: str) -> str:
        return f'{self.build_signature_key()}:{task_id}'


@dataclasses.dataclass
class SimpleTasksRepository(BaseTasksRepository):
    data_source: Dict[str, Any]

    async def set(
        self, value: Any, task_id: str, task_cls: Type[Any] = TaskInfo,
    ) -> None:
        self.data_source[self.build_key(task_id)] = value

    async def get(self, task_id: str, finished_task_cls: Type[Any]) -> Any:
        return self.data_source[self.build_key(task_id)]

    async def lock_signature(self) -> None:
        self.data_source[self.build_signature_key()] = True

    async def lock_args_signature(self, args_signature: str) -> None:
        self.data_source[self.build_key(args_signature)] = True

    async def is_signature_locked(self) -> bool:
        return bool(self.data_source.get(self.build_signature_key(), False))

    async def is_args_locked(self, args_signature: str) -> bool:
        return bool(
            self.data_source.get(self.build_key(args_signature), False)
        )

    async def unlock_signature(self) -> Any:
        return self.data_source.pop(self.build_signature_key())

    async def unlock_args_signature(self, args_signature: str) -> Any:
        return self.data_source.pop(self.build_key(args_signature))


if aioredis is not None:

    @dataclasses.dataclass
    class RedisTasksRepository(BaseTasksRepository):
        data_source: aioredis.Redis

        async def set(
            self, value: Any, task_id: str, task_cls: Type[Any] = TaskInfo,
        ) -> None:
            await self.data_source.set(
                self.build_key(task_id), typed_dict_asjson(value, task_cls)
            )

        async def get(self, task_id: str, finished_task_cls: Type[Any]) -> Any:
            value = await self.data_source.get(self.build_key(task_id))

            if value:
                value = orjson.loads(value)

                if value['status'] == TaskStatusType.RUNNING.value:
                    return as_typed_dict(value, TaskInfo)

                if value['status'] == TaskStatusType.FINISHED.value or (
                    value['status'] == TaskStatusType.ERROR.value
                ):
                    return as_typed_dict(value, finished_task_cls)

            raise KeyError(self.build_key(task_id))

        async def lock_signature(self) -> None:
            await self.data_source.set(self.build_signature_key(), 1)

        async def lock_args_signature(self, args_signature: str) -> None:
            await self.data_source.set(self.build_key(args_signature), 1)

        async def is_signature_locked(self) -> bool:
            return bool(
                await self.data_source.exists(self.build_signature_key())
            )

        async def is_args_locked(self, args_signature: str) -> bool:
            return bool(
                await self.data_source.exists(self.build_key(args_signature))
            )

        async def unlock_signature(self) -> Any:
            return await self.data_source.delete(self.build_signature_key())

        async def unlock_args_signature(self, args_signature: str) -> Any:
            return await self.data_source.delete(
                self.build_key(args_signature)
            )

        async def close(self) -> None:
            self.data_source.close()
            await self.data_source.wait_closed()

    async def get_redis_tasks_repository(
        server_id: uuid.UUID, signature: str, uri: str
    ) -> RedisTasksRepository:
        data_source = await aioredis.create_redis_pool(uri)
        return RedisTasksRepository(server_id, signature, data_source)


TASKS_DB: Dict[str, Any] = {}
