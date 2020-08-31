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
    List,
    Optional,
    Type,
    TypedDict,
)

import orjson
from jsondaora import as_typed_dict, jsondaora, typed_dict_asjson

from ..asgi.router import Controller
from ..exceptions import BadRequestError, InvalidTasksRepositoryError
from ..header import Header, LocationHeader
from ..method import MethodType
from ..middlewares import Middlewares
from ..responses import Response, json, see_other
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
                '-'.join((name, getattr(type_, '__name__', str(type_))))
                for name, type_ in annotations.items()
            ]
        ).encode()
    ).hexdigest()[:12]
    tasks_repository_builder = get_tasks_repository_builder(
        tasks_repository_uri, signature
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

    if 'kwargs' not in create_task.__annotations__:
        create_task.__annotations__['kwargs'] = Any

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


def get_tasks_repository_builder(uri: Optional[str], signature: str) -> Any:
    if uri is None:

        async def builder() -> SimpleTasksRepository:
            return SimpleTasksRepository(signature, TASKS_DB)

        return builder

    elif isinstance(uri, str) and uri.startswith('redis://'):
        if aioredis is None:
            raise InvalidTasksRepositoryError("'aioredis' package not found!")

        return partial(
            get_redis_tasks_repository, signature=signature, uri=uri,
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
        resolved_path = kwargs['request'].resolved_path
        controller_annotations = getattr(controller, '__annotations__', {})

        if (
            'kwargs' not in controller_annotations
            and 'request' not in controller_annotations
        ):
            kwargs.pop('request')

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
        lock_response = await make_lock_response(
            tasks_repository, task_id, lock, args_signature, resolved_path
        )

        if lock_response:
            await tasks_repository.close()
            return lock_response

        if lock:
            await tasks_repository.set_locked_task_id(task_id)
        elif args_signature:
            await tasks_repository.set_locked_task_id(task_id, args_signature)

        if asyncio.iscoroutinefunction(controller):
            wrapper_async = make_controller_wrapper_async(
                tasks_repository_builder,
                task_id,
                lock,
                args_signature,
                finished_task_info_cls,
                controller,
                *args,
                **kwargs,
            )
            task_ = asyncio.create_task(wrapper_async())
            task_.add_done_callback(lambda f: f.result())

        else:
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
            future = executor.submit(wrapper)
            future.add_done_callback(lambda f: f.result())

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

        return json(task, status=HTTPStatus.ACCEPTED)

    return create_task


def make_controller_wrapper_async(
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
            await tasks_repository.delete_locked_task_id()
        elif args_signature:
            await tasks_repository.delete_locked_task_id(args_signature)

        await tasks_repository.close()

    return wrapper


def make_controller_wrapper(
    tasks_repository_builder: Callable[[], Awaitable['BaseTasksRepository']],
    task_id: str,
    lock: bool,
    args_signature: Optional[str],
    finished_task_info_cls: Any,
    controller: Any,
    *args: Any,
    **kwargs: Any,
) -> Callable[..., Any]:
    def wrapper() -> Any:
        policy = asyncio.get_event_loop_policy()
        loop = policy.new_event_loop()
        tasks_repository = loop.run_until_complete(tasks_repository_builder())

        try:
            result = controller(*args, **kwargs)
            status = TaskStatusType.FINISHED.value
        except Exception as error:
            logger.exception(
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
            args_signature=task['args_signature'],
        )

        loop.run_until_complete(
            tasks_repository.set(
                finished_task, task_id, finished_task_info_cls,
            )
        )

        if lock:
            loop.run_until_complete(tasks_repository.delete_locked_task_id())
        elif args_signature:
            loop.run_until_complete(
                tasks_repository.delete_locked_task_id(args_signature)
            )

        loop.run_until_complete(tasks_repository.close())

    return wrapper


def make_get_task_results(
    tasks_repository_builder: Callable[[], Awaitable['BaseTasksRepository']],
    finished_task_info_cls: Type[Any],
) -> Callable[..., Coroutine[Any, Any, TaskInfo]]:
    async def get_task_results(
        task_id: str, **kwargs: Any
    ) -> finished_task_info_cls:  # type: ignore
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


async def make_lock_response(
    tasks_repository: 'BaseTasksRepository',
    task_id: str,
    lock: bool,
    args_signature: Optional[str],
    resolved_path: str,
) -> Optional[Response]:
    headers: List[Header] = []
    locked_task_id = None
    lock_type = None

    if lock:
        locked_task_id = await tasks_repository.get_locked_task_id()
        lock_type = LockType.SIGNATURE

    elif args_signature:
        locked_task_id = await tasks_repository.get_locked_task_id(
            args_signature
        )
        lock_type = LockType.ARGS_SIGNATURE

    if locked_task_id and lock_type:
        headers.append(
            LocationHeader(f'{resolved_path}?task_id={locked_task_id}')
        )
        headers.append(LockHeader(lock_type.value))
        return see_other(headers=headers)

    return None


class LockHeader(Header, type=str, http_name='x-apidaora-lock'):
    ...


class LockType(Enum):
    SIGNATURE = 'signature'
    ARGS_SIGNATURE = 'args-signature'


@dataclasses.dataclass
class BaseTasksRepository:
    signature: str
    data_source: Any

    async def set(
        self, value: Any, task_id: str, task_cls: Type[Any] = TaskInfo,
    ) -> None:
        raise NotImplementedError()

    async def get(self, task_id: str, finished_task_cls: Type[Any]) -> Any:
        raise NotImplementedError()

    async def set_locked_task_id(
        self, task_id: str, args_signature: Optional[str] = None
    ) -> None:
        raise NotImplementedError()

    async def delete_locked_task_id(
        self, args_signature: Optional[str] = None
    ) -> None:
        raise NotImplementedError()

    async def close(self) -> None:
        ...

    async def get_locked_task_id(
        self, args_signature: Optional[str] = None
    ) -> Optional[str]:
        raise NotImplementedError()

    def build_lock_key(self, args_signature: Optional[str]) -> str:
        if args_signature:
            return f'apidaora:{self.signature}:{args_signature}'

        return f'apidaora:{self.signature}'

    def build_key(self, task_id: str) -> str:
        return f'apidaora:{self.signature}:{task_id}'


@dataclasses.dataclass
class SimpleTasksRepository(BaseTasksRepository):
    data_source: Dict[str, Any]

    async def set(
        self, value: Any, task_id: str, task_cls: Type[Any] = TaskInfo,
    ) -> None:
        self.data_source[self.build_key(task_id)] = value

    async def get(self, task_id: str, finished_task_cls: Type[Any]) -> Any:
        return self.data_source[self.build_key(task_id)]

    async def set_locked_task_id(
        self, task_id: str, args_signature: Optional[str] = None
    ) -> None:
        self.data_source[self.build_lock_key(args_signature)] = task_id

    async def get_locked_task_id(
        self, args_signature: Optional[str] = None
    ) -> Optional[str]:
        return self.data_source.get(self.build_lock_key(args_signature))

    async def delete_locked_task_id(
        self, args_signature: Optional[str] = None
    ) -> None:
        self.data_source.pop(self.build_lock_key(args_signature), None)


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

        async def set_locked_task_id(
            self, task_id: str, args_signature: Optional[str] = None
        ) -> None:
            await self.data_source.set(
                self.build_lock_key(args_signature), task_id
            )

        async def get_locked_task_id(
            self, args_signature: Optional[str] = None
        ) -> Optional[str]:
            return await self.data_source.get(  # type: ignore
                self.build_lock_key(args_signature)
            )

        async def delete_locked_task_id(
            self, args_signature: Optional[str] = None
        ) -> None:
            await self.data_source.delete(self.build_lock_key(args_signature))

        async def close(self) -> None:
            self.data_source.close()
            await self.data_source.wait_closed()

    async def get_redis_tasks_repository(
        signature: str, uri: str
    ) -> RedisTasksRepository:
        data_source = await aioredis.create_redis_pool(uri)
        return RedisTasksRepository(signature, data_source)


TASKS_DB: Dict[str, Any] = {}
