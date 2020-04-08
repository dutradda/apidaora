from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .header import Header
from .responses import Response


@dataclass
class MiddlewareRequest:
    path_args: Optional[Dict[str, Any]] = None
    query_dict: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Header]] = None
    body: Optional[Any] = None


@dataclass
class Middlewares:
    post_routing: List[Callable[[Dict[str, Any]], None]]
    pre_execution: List[Callable[[MiddlewareRequest], None]]
    post_execution: List[Callable[[Response], None]]
    post_routing = field(default_factory=list)
    pre_execution = field(default_factory=list)
    post_execution = field(default_factory=list)


def make_kwargs_from_requst(request: MiddlewareRequest) -> Dict[str, Any]:
    kwargs = {}

    if request.path_args:
        kwargs.update(request.path_args)
    if request.query_dict:
        kwargs.update(request.query_dict)
    if request.headers:
        kwargs.update(request.headers)
    if request.body:
        kwargs['body'] = request.body

    return kwargs


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

    def __call__(self, response: Response) -> None:
        if isinstance(response.headers, list):
            response.headers.extend(self.headers)

        elif isinstance(response.headers, tuple):
            response.headers = response.headers + self.headers_tuple
