from dataclasses import field
from http import HTTPStatus
from logging import getLogger
from typing import Optional, TypedDict, _TypedDictMeta  # type: ignore

from jsondaora import dataclass_asjson, jsondaora

from apidaora.headers import AsgiHeaders


logger = getLogger(__name__)


@jsondaora
class Headers(TypedDict):
    ...


@jsondaora
class Body(TypedDict):
    ...


class BaseResponse:
    __content_type__: Optional[str] = None


@jsondaora
class Response(BaseResponse):
    status_code: HTTPStatus
    body: Body
    headers: Headers = field(default_factory=Headers)  # type: ignore


@jsondaora
class JSONResponse(Response):
    __content_type__ = 'application/json'


@jsondaora
class HTMLResponse(Response):
    __content_type__ = 'text/html; charset=utf-8'


@jsondaora
class PlainResponse(Response):
    __content_type__ = 'text/plain'


@jsondaora
class AsgiResponse:
    status_code: HTTPStatus
    headers: AsgiHeaders = field(default_factory=list)
    body: bytes = b''


def as_asgi(response: Response) -> AsgiResponse:
    headers_field = type(response).__dataclass_fields__[  # type: ignore
        'headers'
    ]

    headers: AsgiHeaders = (
        as_asgi_headers(response.headers, headers_field.type)
        if response.headers
        else []
    )
    body: bytes = b''

    if response.body:
        if type(response).__content_type__ == JSONResponse.__content_type__:
            body = dataclass_asjson(response.body)

        elif not isinstance(response.body, bytes):
            body = str(response.body).encode()

        if body:
            if type(response).__content_type__ is not None:
                headers.append(
                    (b'Content-Type', type(response).__content_type__.encode())
                )
            headers.append((b'Content-Length', str(len(body)).encode()))

    return AsgiResponse(  # type: ignore
        status_code=response.status_code, headers=headers, body=body
    )


def as_asgi_headers(
    headers: Optional[Headers], headers_type: _TypedDictMeta
) -> AsgiHeaders:
    if headers:
        return [
            (field.replace('_', '-').encode(), str(headers[field]).encode())
            for field in headers_type.__dataclass_fields__.keys()
        ]

    return []
