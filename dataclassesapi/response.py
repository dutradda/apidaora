from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Optional

from dataclassesjson import asjson

from dataclassesapi.request import AsgiHeaders


@dataclass
class Headers:
    ...


@dataclass
class Body:
    ...


@dataclass
class Response:
    status_code: HTTPStatus
    headers: Optional[Headers] = None
    body: Optional[Body] = None


@dataclass
class AsgiResponse:
    status_code: HTTPStatus
    headers: AsgiHeaders = field(default_factory=list)
    body: bytes = b''


def as_asgi(response: Response) -> AsgiResponse:
    headers = as_asgi_headers(response.headers) if response.headers else []
    body = asjson(response.body) if response.body else b''

    if body:
        headers.append((b'content-type', b'application/json'))
        headers.append((b'content-length', str(len(body)).encode()))

    return AsgiResponse(
        status_code=response.status_code, headers=headers, body=body
    )


def as_asgi_headers(headers: Headers) -> AsgiHeaders:
    return [
        (
            field.replace('_', '-').encode(),
            str(getattr(headers, field)).encode(),
        )
        for field in type(headers).__annotations__.keys()
    ]
