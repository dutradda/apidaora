from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Type

import orjson
from dataclassesjson import asdataclass


@dataclass
class PathArgs:
    ...


@dataclass
class Query:
    ...


@dataclass
class Headers:
    ...


@dataclass
class Body:
    ...


@dataclass
class Request:
    path_args: Optional[PathArgs] = None
    query: Optional[Query] = None
    headers: Optional[Headers] = None
    body: Optional[Body] = None


AsgiPathArgs = Dict[str, Any]
AsgiQueryDict = Dict[str, List[str]]
AsgiHeaders = List[Tuple[bytes, bytes]]


def as_request(
    request_cls: Type[Request],
    path_args: AsgiPathArgs = {},
    query_dict: AsgiQueryDict = {},
    headers: AsgiHeaders = [],
    body: bytes = b'',
) -> Request:
    annotations = getattr(request_cls, '__annotations__', {})
    path_args_cls = annotations.get('path_args', PathArgs)
    query_cls = annotations.get('query', Query)
    headers_cls = annotations.get('headers', Headers)
    body_cls = annotations.get('body', Body)

    return request_cls(
        path_args=asdataclass(path_args, path_args_cls),
        query=get_query(query_cls, query_dict),
        headers=get_headers(headers_cls, headers),
        body=asdataclass(orjson.loads(body) if body else {}, body_cls),
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

    return asdataclass(jsondict, cls)  # type: ignore


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

    return asdataclass(jsondict, cls)  # type: ignore
