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


@jsondaora
class Response:
    status_code: HTTPStatus
    headers: Headers = field(default_factory=Headers)  # type: ignore
    body: Optional[Body] = None


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

    body = dataclass_asjson(response.body) if response.body else b''

    if body:
        headers.append((b'content-type', b'application/json'))
        headers.append((b'content-length', str(len(body)).encode()))

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
