import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from logging import Logger, getLogger
from typing import Any, Callable, Iterable, List, Optional, Union

from .header import Header
from .request import Request
from .responses import Response


@dataclass(init=False)
class Middlewares:
    pre_execution: List[Callable[[Request], None]]
    post_execution: List[Callable[[Request, Response], None]]

    def __init__(
        self,
        pre_execution: Optional[
            Union[List[Callable[[Request], None]], Callable[[Request], None]]
        ] = None,
        post_execution: Optional[
            Union[
                List[Callable[[Request, Response], None]],
                Callable[[Request, Response], None],
            ]
        ] = None,
    ):

        if pre_execution is None:
            pre_execution = []

        elif not isinstance(pre_execution, Iterable):
            pre_execution = [pre_execution]

        elif not isinstance(pre_execution, list):
            pre_execution = list(pre_execution)

        if post_execution is None:
            post_execution = []

        elif not isinstance(post_execution, Iterable):
            post_execution = [post_execution]

        elif not isinstance(post_execution, list):
            post_execution = list(post_execution)

        self.pre_execution = pre_execution
        self.post_execution = post_execution


class AllowOriginHeader(
    Header, type=str, http_name='access-control-allow-origin'
):
    ...


class ExposeHeadersHeader(
    Header, type=str, http_name='access-control-expose-headers'
):
    ...


class AllowHeadersHeader(
    Header, type=str, http_name='access-control-allow-headers'
):
    ...


class AllowMethodsHeader(
    Header, type=str, http_name='access-control-allow-methods'
):
    ...


class CorsMiddleware:
    def __init__(
        self,
        *,
        allow_origin: Optional[str] = None,
        expose_headers: Optional[str] = None,
        allow_headers: Optional[str] = None,
        allow_methods: Optional[str] = None,
        servers_all: Optional[str] = '*',
        logger: Logger = getLogger(__name__),
    ):
        if (
            not allow_origin
            and not expose_headers
            and not allow_headers
            and not allow_methods
        ):
            self.headers = [
                AllowOriginHeader(servers_all),
                ExposeHeadersHeader(servers_all),
                AllowHeadersHeader(servers_all),
                AllowMethodsHeader(servers_all),
            ]
        else:
            self.headers = []
            if allow_origin:
                self.headers.append(AllowOriginHeader(allow_origin))
            if expose_headers:
                self.headers.append(ExposeHeadersHeader(expose_headers))
            if allow_headers:
                self.headers.append(AllowHeadersHeader(allow_headers))
            if allow_methods:
                self.headers.append(AllowMethodsHeader(allow_methods))

        self.headers_tuple = tuple(self.headers)
        self.logger = logger

    def __call__(self, request: Request, response: Response) -> None:
        if isinstance(response.headers, list):
            response.headers.extend(self.headers)

        elif isinstance(response.headers, tuple):
            response.headers = response.headers + self.headers_tuple

        elif response.headers is None:
            response.headers = self.headers_tuple


@dataclass(init=False)
class BackgroundTaskMiddleware:
    executor: ThreadPoolExecutor
    logger: Logger

    def __init__(
        self, max_workers: int = 100, logger: Logger = getLogger(__name__),
    ):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.logger = logger

    def __call__(self, request: Request, response: Response) -> None:
        task: Any
        response_tasks: Union[
            Iterable[Callable[[], None]], Callable[[], None]
        ] = []

        if response.ctx:
            response_tasks = response.ctx.get(
                'background_tasks', response_tasks
            )

        if response_tasks and not isinstance(response_tasks, Iterable):
            response_tasks = (response_tasks,)

        for task in response_tasks:
            if asyncio.iscoroutinefunction(task):
                task = task()

            elif not asyncio.iscoroutine(task):
                future = self.executor.submit(task)
                future.add_done_callback(self.done_callback)
                return

            task = asyncio.create_task(task)
            task.add_done_callback(self.done_callback)

    def done_callback(self, future: Any) -> None:
        try:
            future.result()
        except Exception:
            self.logger.exception('Background Task Error')
