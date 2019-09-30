import re
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    DefaultDict,
    Dict,
    Iterable,
    Optional,
    Pattern,
)

from ..exceptions import MethodNotFoundError, PathNotFoundError
from ..method import MethodType
from .request import Request
from .response import Response


Caller = Callable[..., Any]


@dataclass
class Route:
    path_pattern: str
    method: MethodType
    caller: Caller
    has_query: bool = False
    has_headers: bool = False
    has_body: bool = False


@dataclass
class ResolvedRoute:
    route: Route
    path_args: Dict[str, Any]
    path: str


def split_path(path: str) -> Iterable[str]:
    return path.strip(' /').split('/')
