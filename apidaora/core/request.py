from collections.abc import Iterable
from dataclasses import dataclass
from logging import getLogger
from typing import Any, Dict, Optional, Type, TypedDict

import orjson
from jsondaora import (
    as_typed_dict,
    as_typed_dict_field,
    asdataclass,
    jsondaora,
)

from ..content import ContentType
from .headers import AsgiHeaders, AsgiPathArgs, AsgiQueryDict, Headers


logger = getLogger(__name__)


@jsondaora
class PathArgs(TypedDict):
    ...


@jsondaora
class Query(TypedDict):
    ...


@jsondaora
class Body(TypedDict):
    ...


@dataclass
class Request:
    path_args: PathArgs
    query: Query
    headers: Headers
    body: Optional[Body]


def as_request(
    request_cls: Type[Request],
    body: bytes,
    path_args: AsgiPathArgs = {},
    query_dict: AsgiQueryDict = {},
    headers: AsgiHeaders = [],
) -> Request:
    annotations = getattr(request_cls, '__annotations__', {})
    path_args_cls = annotations.get('path_args', PathArgs)
    query_cls = annotations.get('query', Query)
    headers_cls = annotations.get('headers', Headers)
    body_cls = annotations.get('body', Body)
    request_path_args = as_typed_dict(path_args, path_args_cls)
    request_query = get_query(query_cls, query_dict)
    request_headers = get_headers(headers_cls, headers)
    content_type = request_headers.get('content_type')
    parsed_body: Any = None

    if content_type is None or content_type is ContentType.APPLICATION_JSON:
        parsed_body = orjson.loads(body) if body else {}
        parsed_body = as_typed_dict_field(parsed_body, 'body', body_cls)
    else:
        parsed_body = body.decode()

    return asdataclass(  # type: ignore
        dict(
            path_args=request_path_args,
            query=request_query,
            headers=request_headers,
            body=parsed_body if parsed_body else None,
        ),
        request_cls,
        skip_fields=('body',),
    )


def get_query(cls: Type[Query], query_dict: AsgiQueryDict) -> Query:
    jsondict: Dict[str, Any] = {}
    annotations = getattr(cls, '__annotations__', {})

    for key in annotations.keys():
        values = query_dict.get(key)

        if values:
            jsondict[key] = (
                values[0] if isinstance(values, Iterable) else values
            )
        else:
            jsondict[key] = values

    return as_typed_dict(jsondict, cls)  # type: ignore


def get_headers(cls: Type[Headers], headers: AsgiHeaders) -> Headers:
    jsondict = {}
    annotations = getattr(cls, '__annotations__', {})

    for key in annotations.keys():
        for key_h, value in headers:
            if key == key_h.decode().lower().replace('-', '_'):
                break
        else:
            continue

        jsondict[key] = value.decode()

    return as_typed_dict(jsondict, cls)  # type: ignore
