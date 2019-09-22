from dataclasses import dataclass, field
from http import HTTPStatus
from logging import getLogger
from typing import (  # type: ignore
    Any,
    Dict,
    Optional,
    TypedDict,
    _TypedDictMeta,
)

from jsondaora import dataclass_asjson, jsondaora

from ..content import ContentType
from .headers import AsgiHeaders, Headers


logger = getLogger(__name__)


@jsondaora
class Body(TypedDict):
    error: Dict[str, Any]


@dataclass
class Response:
    body: Body
    headers: Headers = field(default_factory=Headers)  # type: ignore


Response.__content_type__: Optional[ContentType] = None  # type: ignore
Response.__status_code__: HTTPStatus = HTTPStatus.OK  # type: ignore


@dataclass
class JSONResponse(Response):
    __content_type__ = ContentType.APPLICATION_JSON


@dataclass
class HTMLResponse(Response):
    __content_type__ = ContentType.TEXT_HTML


@dataclass
class PlainResponse(Response):
    __content_type__ = ContentType.TEXT_PLAIN


@dataclass
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
        if (
            type(response).__content_type__  # type: ignore
            == JSONResponse.__content_type__
        ):
            body = dataclass_asjson(response.body)

        elif not isinstance(response.body, bytes):
            body = str(response.body).encode()

        if body:
            if type(response).__content_type__:  # type: ignore
                headers.append(
                    (
                        b'Content-Type',
                        type(
                            response
                        ).__content_type__.value.encode(),  # type: ignore
                    )
                )

            headers.append((b'Content-Length', str(len(body)).encode()))

    return AsgiResponse(
        status_code=response.__status_code__,  # type: ignore
        headers=headers,
        body=body,
    )


def as_asgi_headers(
    headers: Optional[Headers], headers_type: _TypedDictMeta
) -> AsgiHeaders:
    if headers:
        return [
            (field.replace('_', '-').encode(), str(value).encode())
            for field, value in headers.items()
        ]

    return []
